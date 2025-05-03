from datetime import timedelta, datetime
from typing import Annotated, Type

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy import select

from .exceptions import unauthorized_exception

from database.database import get_async_session
from src.config import SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE
from jose import jwt, JWTError
from database.models import User
import random
from typing import Annotated
from fastapi import Depends

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def login_response(user_id: int, auth_token: str):
    access_token = create_jwt_token(user_id=user_id,
                                    expires_in=timedelta(minutes=ACCESS_TOKEN_EXPIRE),
                                    auth_token=auth_token)
    refresh_token = create_jwt_token(user_id=user_id,
                                     expires_in=timedelta(days=REFRESH_TOKEN_EXPIRE),
                                     auth_token=auth_token)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


async def authenticate_user(email: EmailStr, password: str, db: db_dependency) -> User | bool:
    """
    Authenticate user function

    :param email: email entered by the user
    :param password: password entered by the user
    :param db: object of db session
    :return: user object if user exist
    """
    query = await db.execute(select(User).filter(User.email == email))
    user = query.scalar()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


async def get_user_by_id(user_id: int, db: db_dependency) -> User | None:
    # query = await db.execute(select(User).filter(User.id == user_id))
    # user = query.scalar_one()
    user = await db.get(User, user_id)
    return user



def create_jwt_token(user_id: int, auth_token: str, expires_in: timedelta) -> jwt:
    """
    Encoding access token

    :param auth_token:
    :param user_id: authenticated user id
    :param expires_in: token lifetime
    :return: encoded jwt token
    """
    encode = {'id': user_id, 'auth_token': auth_token, 'exp': datetime.utcnow() + expires_in}
    return jwt.encode(encode, key=SECRET, algorithm=ALGORITHM)


async def authorize_required(token: Annotated[str, Depends(oauth2_bearer)],
                             db: db_dependency) -> int:
    """
    Dependency for protected routes

    EXAMPLE OF USE:
    @router.get('/', status_code=status.HTTP_200_OK)
    async def protected_route(user_id: Annotated[int, Depends(authorize_required)[0]]):
        return {'Hello': user_id}

    :param db:
    :param token: access_token
    :return: user_id or HTTPException
    """
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        auth_token: str = payload.get('auth_token')
        user = await db.get(User, user_id)
        if user_id is None:
            raise unauthorized_exception
        if user is None or user.auth_token != auth_token:
            raise unauthorized_exception
        return user_id
    except JWTError:
        raise unauthorized_exception


def ext_authorize_required(token: Annotated[str, Depends(oauth2_bearer)],
                           auth_dependency: Annotated[int, Depends(authorize_required)]) -> tuple[int, str]:
    auth_token: str = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get('auth_token')
    return auth_dependency, auth_token


def get_auth_token():
    return '%030x' % random.randrange(16 ** 30)

BaseAuthDep = Annotated[int, Depends(authorize_required)]
ExtAuthDep = Annotated[tuple[int, str], Depends(ext_authorize_required)]
