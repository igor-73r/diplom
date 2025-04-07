from typing import Annotated
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List

pk = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[pk]
    username: Mapped[str] = mapped_column(String(length=50), nullable=False)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)

    full_data: Mapped[List["FullData"]] = relationship(back_populates="user")
    chunks: Mapped[List["Chunks"]] = relationship(back_populates="user")


class FullData(Base):
    __tablename__ = "full_data"

    id: Mapped[pk]
    name: Mapped[str] = mapped_column(String(length=120), nullable=False)
    hash_func: Mapped[str] = mapped_column(String(length=64), nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    chunk_quantity: Mapped[int] = mapped_column(nullable=False)
    user_owner: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="full_data")
    chunks: Mapped[List["Chunks"]] = relationship(back_populates="full_data")


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
    name: Mapped[str] = mapped_column(String(length=64), nullable=False)  # uuid.bin
    chunk_ordinal_number: Mapped[int] = mapped_column(nullable=False)
    user_holder_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    full_data_id: Mapped[int] = mapped_column(ForeignKey("full_data.id"), nullable=False)
    is_copy: Mapped[bool] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="chunks")
    full_data: Mapped["FullData"] = relationship(back_populates="chunks")
