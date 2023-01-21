from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from db.base import new_async_engine, new_session_maker, initialize_schemas
import db.models
# from db.FSMStorage import Storage
from config import *
from text_templates import *
from sqlalchemy.engine import URL
import asyncio


async def main():
    # db initialization
    db_url = URL.create(
        "postgresql+asyncpg",
        host=DB_HOST,
        port=DB_PORT,
        username=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    engine = new_async_engine(db_url)
    sm = new_session_maker(engine)
    await initialize_schemas(engine)

# bot initialization
# bot = Bot(token=TOKEN_TELEGRAM_ADMIN)
# storage = Storage("admin", sm)
# dp = Dispatcher(bot, storage=storage)
#
#
# @dp.message_handler(commands=['start'])
# async def process_start_command(message: types.Message):
#     await message.reply(TMP_START)
#
#
# @dp.message_handler(commands=['help'])
# async def process_help_command(message: types.Message):
#     await message.reply(TMP_HELP)
#
#
# if __name__ == '__main__':
#     executor.start_polling(dp)

if __name__ == '__main__':
    asyncio.run(main())
