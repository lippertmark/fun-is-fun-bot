from admin_core.bot_handlers.registration import reg_admin_menu_handlers
from admin_core.bot_middlewares.sessionmaker import DbMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot
from sqlalchemy.engine import URL
from db.base import new_async_engine, new_session_maker
from db.FSMStorage import Storage
from config import *

# db initialization
db_url = URL.create("postgresql+asyncpg",
                    host=DB_HOST,
                    port=DB_PORT,
                    username=DB_USERNAME,
                    password=DB_PASSWORD,
                    database=DB_NAME)
engine = new_async_engine(db_url)
sm = new_session_maker(engine)

# bot initialization
bot = Bot(token=TOKEN_TELEGRAM_ADMIN)
storage = Storage("admin", sm)
dp = Dispatcher(bot, storage=storage)
# registering middleware
dp.middleware.setup(DbMiddleware(sm))  # necessary to provide handlers access to db
# registering handlers
reg_admin_menu_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dp)
