from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

BaseModel = declarative_base()


def new_async_engine(url: [URL | str]) -> AsyncEngine:
    """
    Create instance of async engine.
    The only parameter is URL to database.

    :param url:
    :return:
    """
    return create_async_engine(url=url, encoding="UTF-8", echo=True, pool_pre_ping=True)


def new_session_maker(engine: AsyncEngine) -> sessionmaker:
    """
    Create instance of sessionmaker for async engine.

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
