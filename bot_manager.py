import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery
from event_module import check_user_is_aproved
from config import *
# Enable logging
logging.basicConfig(level=logging.INFO)

# Define a list of approved users
approved_users = []


# Initialize bot and dispatcher
bot = Bot(TOKEN_TELEGRAM_MANAGER)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)




# Define a middleware class to handle new members joining the chat
class MemberJoinMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message, data):
        if message.new_chat_members:
            for member in message.new_chat_members:
                if check_user_is_aproved(message.chat.id, member.id):
                    await bot.kick_chat_member(chat_id=message.chat.id, user_id=member.id)

# Use the middleware in the dispatcher
dp.middleware.setup(MemberJoinMiddleware())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
