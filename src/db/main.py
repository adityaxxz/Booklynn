from sqlmodel import text
from sqlalchemy.ext.asyncio import async_engine_from_config, async_session, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import config
from sqlmodel import SQLModel
from typing import AsyncGenerator

async_engine = create_async_engine(
    url=config.DATABASE_URL,
    echo=True
)


async def initdb():
    """create a connection to our db"""

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # statement = text("select 'Hello World'")
        # result = await conn.execute(statement)
        # print(result)



async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session





