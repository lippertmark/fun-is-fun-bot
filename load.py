import os
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
from config import *
from sqlalchemy.engine import URL
from db.base import new_async_engine, new_session_maker
from db.FSMStorage import Storage
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path)
# TOKEN = os.getenv("TOKEN_TELEGRAM")
# PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")

db_url = URL.create("postgresql+asyncpg",
                    host=DB_HOST,
                    port=DB_PORT,
                    username=DB_USERNAME,
                    password=DB_PASSWORD,
                    database=DB_NAME)
engine = new_async_engine(db_url, echo=False)
sm = new_session_maker(engine)


storage = Storage("client", sm)
# storage = MemoryStorage()
bot = Bot(token=TOKEN_TELEGRAM_CLIENT, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
