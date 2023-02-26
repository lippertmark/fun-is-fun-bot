import os
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from db.base import new_async_engine, new_session_maker
from db.FSMStorage import Storage
from aiogram.contrib.fsm_storage.memory import MemoryStorage

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
TOKEN_TELEGRAM_CLIENT = os.getenv("TOKEN_TELEGRAM_CLIENT")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")

db_url = URL.create("postgresql+asyncpg",
                    host=os.getenv('DB_HOST'),
                    port=os.getenv('DB_PORT'),
                    username=os.getenv('DB_USERNAME'),
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME'))
engine = new_async_engine(db_url, echo=False)
sm = new_session_maker(engine)


storage = Storage("client", sm)
bot = Bot(token=TOKEN_TELEGRAM_CLIENT, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
