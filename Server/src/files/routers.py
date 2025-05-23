from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile
from starlette import status
from Server.src.models import User, FullData, Chunks, Node
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi.responses import FileResponse
from sqlalchemy import delete

from Server.src.database import get_async_session
from .schemas import FullFile, AddChunk, FullFileResponse, GetNode, CreateNode
import os
from Server.src.config import base_net_path_to_share_folder, base_share_folder_name

db_dependency = Annotated[AsyncSession, Depends(get_async_session)]


router = APIRouter(
    prefix='/data',
    tags=['files'],
)


@router.post('/add_node', status_code=status.HTTP_201_CREATED, response_model=GetNode)
async def add_node(db: db_dependency, node: CreateNode):
    db_node = Node(pc_name=node.pc_name)
    try:
        db.add(db_node)
        await db.commit()
        await db.refresh(db_node)
    except exc.SQLAlchemyError as e:
        # Node already exist
        return db_node
    else:
        return db_node

@router.get("/get_node/{node_name}", status_code=status.HTTP_200_OK)
async def get_node(db: db_dependency, node_name: str):
    try:
        node = await db.execute(select(Node).filter_by(pc_name=node_name))
        return node.scalars().one_or_none()
    except ValueError as e:
        raise e


@router.get("/get_nodes", status_code=status.HTTP_200_OK)
async def get_nodes(db: db_dependency):
    try:
        node = await db.execute(select(Node))
        return node.scalars().all()
    except ValueError as e:
        raise e


@router.post('/add_full_file', status_code=status.HTTP_201_CREATED, response_model=FullFileResponse)
async def add_full_file(db: db_dependency, file: FullFile):
    db_full_file = FullData(
        name=file.name,
        hash_func=file.hash_func,
        size=file.size,
        chunk_quantity=file.chunk_quantity,
        user_owner=file.user_owner
    )
    try:
        db.add(db_full_file)
        await db.commit()
        await db.refresh(db_full_file)
    except exc.SQLAlchemyError as e:
        # User already exist
        return "File ALREADY EXIST"
    else:
        return db_full_file

from sqlalchemy import exc, select


@router.get('/get_files/{user_id}')
async def get_files_by_user_id(db: db_dependency, user_id: int):
    try:
        files = await db.execute(select(FullData).filter_by(user_owner=user_id))
        return files.scalars().all()
    except ValueError as e:
        raise e


def buils_chunk_path(name):
    return f"//{name}{base_net_path_to_share_folder}/{base_share_folder_name}"

@router.post('/upload_chunk', status_code=status.HTTP_201_CREATED)
async def upload_chunk(db: db_dependency,
                       file: UploadFile,
                       chunk_data: AddChunk = Depends()):
    """
    Тут должна быть попытка закинуть файл пользователю держателю, и если все успешно, тогда добавляем в бд
    """

    node = await db.get(Node, chunk_data.folder_holder_id)
    user_dir = os.path.join(buils_chunk_path(node.pc_name), f"{chunk_data.name}.bin")
    try:
        with open(user_dir, 'wb') as f:
            f.write(file.file.read())
            f.close()
    except Exception as e:
        raise e

    db_chunk = Chunks(
        name=chunk_data.name,
        chunk_ordinal_number=chunk_data.chunk_ordinal_number,
        folder_holder_id=chunk_data.folder_holder_id,
        full_data_id=chunk_data.full_data_id,
    )
    try:
        db.add(db_chunk)
        await db.commit()
        await db.refresh(db_chunk)
    except exc.SQLAlchemyError as e:
        # User already exist
        return "Chunk ALREADY EXIST"
    else:
        return db_chunk

@router.get('/get_chunks/{parent_file_id}')
async def get_chunks(db: db_dependency, parent_file_id: int):
    chunks = await db.execute(select(Chunks).filter_by(full_data_id=parent_file_id))
    return chunks.scalars().all()


@router.get('/download_chunk/{chunk_id}')
async def download_chunk(db: db_dependency, chunk_id: int):
    """
    Мб в связи с тем, что решили не делать упор на сетевую инфраструктуру, стоить сделать так, чтобы по запросы
    пользователю возвращались пути до всех чанков, а их скачивани (по сути просто перенос с сетевого диска)
    сделать каким нибудь shutil или через os

    :param db:
    :param chunk_id:
    :return:
    """

    chunk = await db.get(Chunks, chunk_id)
    node = await db.get(Node, chunk.folder_holder_id)

    chunk_file = os.path.join(buils_chunk_path(node.pc_name), f"{chunk.name}.bin")
    return FileResponse(
        path=chunk_file,
        filename=chunk.name,  # Имя файла для скачивания
        media_type="application/octet-stream"  # Универсальный MIME-тип
    )


@router.delete('/delete_file/{parent_file_id}')
async def delete_file(db: db_dependency, parent_file_id: int):
    chunks = await db.execute(select(Chunks).filter_by(full_data_id=parent_file_id))
    parent = await db.get(FullData, parent_file_id)
    await db.execute(delete(Chunks).where(Chunks.full_data_id == parent_file_id))
    for chunk_data in chunks.scalars().all():
        node = await db.get(Node, chunk_data.folder_holder_id)
        user_dir = os.path.join(buils_chunk_path(node.pc_name), f"{chunk_data.name}.bin")
        try:
            os.remove(user_dir)
        except Exception as e:
            raise e
    await db.delete(parent)
    await db.commit()
    return "done"

