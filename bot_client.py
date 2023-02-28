from load import dp
import client_core.handlers
from client_core.handlers import notif, start, without_sub, for_subscribers
from aiogram.utils import executor

notif.reg_notif_handlers(dp)
start.reg_default_handlers(dp)
without_sub.reg_without_sub_handlers(dp)
for_subscribers.reg_for_subs_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
