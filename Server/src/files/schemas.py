from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr

class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str


class BaseUser(BaseModel):
    id: int
    username: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserData(BaseModel):
    id: int
    first_name: str
    second_name: str
    email: str


class UpdatePassword(BaseModel):
    previous_password: str
    new_password: str
    repeat_new_password: str

class UploadDone(BaseModel):
    filename: str


class FullFile(BaseModel):
    name: str
    hash_func: str
    size: int
    chunk_quantity: int
    user_owner: int

class FullFileResponse(BaseModel):
    id: int
    name: str
    hash_func: str
    size: int
    chunk_quantity: int
    user_owner: int



class AddChunk(BaseModel):
    name: str
    chunk_ordinal_number: int
    user_holder_id: int
    full_data_id: int
    is_copy:  bool


class AuthUser(BaseModel):
    email: EmailStr
    password: str
