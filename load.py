import os
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
TOKEN = os.getenv("TOKEN_TELEGRAM")
PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")

storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
