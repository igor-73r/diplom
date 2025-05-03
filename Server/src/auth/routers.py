from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from Server.src.models import User
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import exc
from fastapi.exceptions import ResponseValidationError

from .schemas import CreateUser, BaseUser, Token, UpdatePassword
from .auth import (bcrypt_context, db_dependency, authenticate_user,
                   login_response, get_user_by_id, get_auth_token)
from .auth_dependencies import BaseAuthDep, ExtAuthDep
from .exceptions import credentials_exception, unfilled_profile

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=BaseUser)
async def create_user(db: db_dependency, create_user_request: CreateUser) -> User:
    """
    Base create (register) user function

    :param db: object of db session
    :param create_user_request: CreateUser schema:
        class CreateUser(BaseModel):
            email: EmailStr
            password: str
    :return: User object limited by BaseUser schema:
            class BaseUser(BaseModel):
                id: int
                first_name: str
                email: EmailStr
    """
    db_user = User(
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        auth_token=get_auth_token()
    )
    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except exc.SQLAlchemyError as e:
        # User already exist
        raise e
    else:
        return db_user


@router.post('/token', response_model=Token)
async def login_for_access_token(login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency) -> dict:
    """
    Auth user function that returns access token

    :param login_form: built-in FastApi form (login_form.username is actually an email,
           but the username field is used in the built-in FastApi form)
    :param db: object of db session
    :return: dict with access token or raise HTTPException
    """
    user = await authenticate_user(login_form.username, login_form.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="BAD_CREDENTIALS")  # TODO change status code
    return login_response(user_id=user.id, auth_token=user.auth_token)


@router.get('/refresh', response_model=Token)
async def refresh_access_token(data: ExtAuthDep) -> dict:
    """
    A refresh token is passed to this function from the user request,
    in case of its validity, the updated tokens are returned
    :param data: obtained from decoded jwt token from authorize_required function. Contains user_id and auth_token
    :return: dict from "Token" scheme
    """
    return login_response(user_id=data[0], auth_token=data[1])


@router.get('/get_current_user', response_model=BaseUser)
async def get_current_user(user_id: BaseAuthDep, db: db_dependency) -> User:
    """
    Function is used to get the object of the current authorized user, as well as to check the relevance of tokens
    :param user_id: obtained from decoded jwt token from authorize_required function
    :param db: db dependency
    :return: User object
    """
    return await get_user_by_id(user_id=user_id, db=db)


@router.put('/update_password', status_code=status.HTTP_200_OK)
async def update_password(db: db_dependency, user_id: BaseAuthDep, passwords: UpdatePassword):
    user = await db.get(User, user_id)
    if (bcrypt_context.verify(passwords.previous_password, user.hashed_password) and
            passwords.new_password == passwords.repeat_new_password):
        user.hashed_password = bcrypt_context.hash(passwords.new_password)
        user.auth_token = get_auth_token()
        await db.commit()
    else:
        raise credentials_exception


