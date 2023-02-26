from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from db.models import BaseModel
from typing import Union
from config import *
import asyncio


def new_async_engine(url: Union[URL, str], echo: bool = False) -> AsyncEngine:
    """
    Create an instance of async engine by url.
    :param url:
    :param echo:
    :return:
    """

    return create_async_engine(url=url, echo=echo, pool_pre_ping=True)


def new_session_maker(engine: AsyncEngine) -> sessionmaker:
    """
    Create an instance of sessionmaker for async engine.
    :param engine:
    :return:
    """
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def initialize_schemas(engine: AsyncEngine) -> None:
    """
    Initializes tables for new schemas from metadata of BaseModel.
    Will NOT remove or update tables that already exist.
    :param engine:
    :return:
    """
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


if __name__ == '__main__':
    # To initialize schemas run base.py directly

    db_url = URL.create("postgresql+asyncpg",
                        host=DB_HOST,
                        port=DB_PORT,
                        username=DB_USERNAME,
                        password=DB_PASSWORD,
                        database=DB_NAME)
    async_engine = new_async_engine(db_url)
    asyncio.run(initialize_schemas(async_engine))
