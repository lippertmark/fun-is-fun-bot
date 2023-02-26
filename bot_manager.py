import os
import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares import BaseMiddleware
from event_module import check_user_is_approved
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
MANAGER_BOT_TOKEN = os.getenv('MANAGER_BOT_TOKEN')

# Enable logging
logging.basicConfig(level=logging.INFO)

# Define a list of approved users
approved_users = []

# Define the bot's token
API_TOKEN = MANAGER_BOT_TOKEN

# Initialize bot and dispatcher
bot = Bot(API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Define a middleware class to handle new members joining the chat
class MemberJoinMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message, data):
        if message.new_chat_members:
            for member in message.new_chat_members:
                if not check_user_is_approved(message.chat.id, member.id):
                    await bot.kick_chat_member(chat_id=message.chat.id, user_id=member.id)


# Use the middleware in the dispatcher
dp.middleware.setup(MemberJoinMiddleware())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
