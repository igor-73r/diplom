from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    email: EmailStr
    password: str


class BaseUser(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserData(BaseModel):
    id: int
    email: str


class UpdatePassword(BaseModel):
    previous_password: str
    new_password: str
    repeat_new_password: str


class UpdateEmail(BaseModel):
    email: EmailStr
