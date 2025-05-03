from fastapi import HTTPException
from starlette import status

unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="UNAUTHORIZED",
    headers={"WWW-Authenticate": "Bearer"},
)

credentials_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="WRONG CREDENTIALS",
    headers={"WWW-Authenticate": "Bearer"},
)

unfilled_profile = HTTPException(
    status_code=status.HTTP_417_EXPECTATION_FAILED,
    detail="UNFILLED PROFILE",
    headers={"WWW-Authenticate": "Bearer"},
)

