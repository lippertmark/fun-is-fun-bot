from load import dp
import client_core.handlers
from aiogram.utils import executor

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
