from typing import Annotated
from fastapi import Depends
from .auth import authorize_required, ext_authorize_required

BaseAuthDep = Annotated[int, Depends(authorize_required)]
ExtAuthDep = Annotated[tuple[int, str], Depends(ext_authorize_required)]
