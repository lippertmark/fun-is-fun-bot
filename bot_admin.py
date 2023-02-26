import os
from admin_core.bot_handlers.registration import reg_admin_menu_handlers
from admin_core.bot_handlers.menu import reg_menu_handlers
from admin_core.bot_middlewares.sessionmaker import DbMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot
from sqlalchemy.engine import URL
from db.base import new_async_engine, new_session_maker
from db.FSMStorage import Storage


TOKEN_TELEGRAM_ADMIN = os.getenv('TOKEN_TELEGRAM_ADMIN')

# db initialization
db_url = URL.create("postgresql+asyncpg",
                    host=os.getenv('DB_HOST'),
                    port=os.getenv('DB_PORT'),
                    username=os.getenv('DB_USERNAME'),
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME'))
engine = new_async_engine(db_url, echo=False)
sm = new_session_maker(engine)

# bot initialization
bot = Bot(token=TOKEN_TELEGRAM_ADMIN)
storage = Storage("admin", sm)
dp = Dispatcher(bot, storage=storage)
# registering middleware
dp.middleware.setup(DbMiddleware(sm))  # necessary to provide handlers access to db
# registering handlers
reg_admin_menu_handlers(dp)
reg_menu_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dp)
