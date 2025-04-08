from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

async_engine = create_async_engine("sqlite+aiosqlite:///sharespace.db")
AsyncSessionLocal = async_sessionmaker(bind=async_engine, autoflush=False)


async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
