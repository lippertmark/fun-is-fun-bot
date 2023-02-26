'''
файл нужно запускать каждую минуту для проверки чатов видеочатов через крон
'''
from config import *
from event_module import *


def check_similarity(date1, date2):
    return date1.year == date2.year and date1.day == date2.day and \
           date1.month == date2.month and date1.hour == date2.hour and date1.minute == date2.minute


import datetime, pytz

from db_client.utils import get_all_time_delete

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import asyncio
from db_client.utils import *

sender = Bot(token=TOKEN_TELEGRAM_CLIENT)
bot_mаnager = Bot(TOKEN_TELEGRAM_MANAGER)


async def send_telegram_message(chat_id, message):
    await sender.send_message(chat_id=chat_id, text=message)


async def delete_from_chat(chat_id, user_id):
    await bot_mаnager.kick_chat_member(chat_id=chat_id, user_id=user_id)


# asyncio.run(send_telegram_message(338600505, "Hey, person!"))

time_delete_items = get_all_time_delete()
print(time_delete_items)
now = datetime.datetime.now(pytz.timezone("Europe/Moscow"))

for slot in time_delete_items:
    if now > slot['start_time'] and slot['already_added'] == False:
            link = give_link_to_invite(slot['chat_id'], slot['user_id'])
            asyncio.run(send_telegram_message(slot['user_id'], f"Заходи на созвон со звездой: {link}"))
            update_time_delete(slot['id'], {"already_added": True})
    elif now > slot['end_time']:
        asyncio.run(delete_from_chat(slot['chat_id'], slot['user_id']))
        delete_time_delete(slot['id'])
        print(f"deleted user{slot['user_id']}")
