from load import dp
import handlers
from aiogram.utils import executor

if __name__ == '__main__':
    executor.start_polling(dp)
