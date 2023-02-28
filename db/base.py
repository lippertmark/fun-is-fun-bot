import os
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from db.models import BaseModel
from dotenv import load_dotenv
from typing import Union
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
    dotenv_path = os.path.join(os.path.dirname(__file__), '..',  ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    db_url = URL.create("postgresql+asyncpg",
                        host=os.getenv('DB_HOST'),
                        port=os.getenv('DB_PORT'),
                        username=os.getenv('DB_USERNAME'),
                        password=os.getenv('DB_PASSWORD'),
                        database=os.getenv('DB_NAME'))
    print(db_url)
    async_engine = new_async_engine(db_url)
    asyncio.run(initialize_schemas(async_engine))
