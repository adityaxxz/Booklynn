from sqlmodel import text
from sqlalchemy.ext.asyncio import async_engine_from_config, async_session, create_async_engine, AsyncSession, async_sessionmaker
from src.config import Config
from sqlmodel import SQLModel
from typing import AsyncGenerator

async_engine = create_async_engine(
    url=Config.DATABASE_URL,
    echo=True
)


async def initdb():
    """create a connection to our db"""
    # Import models here to avoid circular imports
    from src.db.models import User
    
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # statement = text("select 'Hello World'")
        # result = await conn.execute(statement)
        # print(result)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    from sqlmodel.ext.asyncio.session import AsyncSession
    async_session = async_sessionmaker(
        bind=async_engine, 
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session




