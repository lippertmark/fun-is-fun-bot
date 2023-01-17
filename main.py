from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import *
from text_templates import *

bot = Bot(token=TOKEN_TELEGRAM)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(TMP_START)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(TMP_HELP)


if __name__ == '__main__':
    executor.start_polling(dp)
