from load import dp
import handlers
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

dp.middleware.setup(LoggingMiddleware())

if __name__ == '__main__':
    executor.start_polling(dp)
