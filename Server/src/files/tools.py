from typing import Annotated
from fastapi import Depends
from sqlalchemy import select

from Server.src.models import Node
from sqlalchemy.ext.asyncio import AsyncSession

from Server.src.database import get_async_session
from Server.src.models import Node
from Server.src.config import base_net_path_to_share_folder, base_share_folder_name


db_dependency = Annotated[AsyncSession, Depends(get_async_session)]

def get_chunks_dirs():
    pass


async def get_node_by_id(db: db_dependency, node_id: int):
    return






if __name__ == '__main__':
    test()
