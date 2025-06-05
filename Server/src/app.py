import asyncio

from fastapi import FastAPI
from Server.src.files.routers import router as file_routers
from Server.src.models import Base
from Server.src.database import async_engine
from Server.src.auth.routers import router as auth_routers

import uvicorn


app = FastAPI(
    title="ShareSpace"
)

app.include_router(router=file_routers)
app.include_router(router=auth_routers)


async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(init_models())
    uvicorn.run("app:app")
