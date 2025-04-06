from typing import Annotated
from fastapi import APIRouter

from src.database import async_engine

from sqlalchemy import ForeignKey, String, Date, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List

pk = Annotated[int, mapped_column(primary_key=True)]

router = APIRouter(
    prefix='/db',
    tags=['db'],
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[pk]
    username: Mapped[str] = mapped_column(String(length=50), nullable=False)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    auth_token: Mapped[str | None]  # remove None

class DataMap(Base):
    __tablename__ = "full_data"

    id: Mapped[pk]
    name: Mapped[str]
    hash_func: Mapped[str]
    size: Mapped[int]
    chunk_quantity: Mapped[int]
    user_owner: ForeignKey


class Chunks(Base):
    """
    Схема такая:
    На стороне хоста хранится чанк формата 3422b448-2460-4fd2-9183-8000de6f8343.bin
    Пользователь хочет скачать свой файл id = 2:
        1. Делаем SELECT * FROM chunks WHERE full_data_id==2 AND is_copy==False
        2. Скачиваем чанки у других пользователей (пока хз как)
        3. Проверяем что количество соответствует chunk_quantity из full_data
        4. Если все ок, бахаем пары (chunk_name, ordinal_number) сортируем и объединяем
        5. Если не ок, определяем недоступный чанк, и пытаемся скачать копию
        6. Дальше либо как в п.4 либо фиксируем убытки
    """
    __tablename__ = "chunks"

    id: Mapped[pk]
    name: Mapped[str]  # uuid.bin
    chunk_number: Mapped[int]
    user_holder_id: ForeignKey
    full_data_id: ForeignKey
    is_copy: Mapped[bool]


