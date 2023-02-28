from aiogram.dispatcher import FSMContext
from aiogram import types
import i18n
from load import bot, dp
from db.utils import *
from event_module import give_link_to_invite
import client_core.keybords as kb
from db.utils import get_slots
i18n.load_path.append('.')
i18n.set('locale', 'ru')


async def delete_all_messages(user_id, state):
    async with state.proxy() as data:
        try:
            for msg in data['msg']:
                await bot.delete_message(user_id, msg)
        finally:
            pass


async def delete_last_message(user_id, state):
    async with state.proxy() as data:
        await bot.delete_message(user_id, data['msg'][len(data['msg']) - 1])


def is_swipeable(code, page, length):
    return code == '<' and page > 0 or code == '>' and (length - page * 10) > 10


async def add_booking(callback_query: types.CallbackQuery, state: FSMContext, slot_id):
    event_id = int(callback_query.data.split('-')[1])
    event = await get_event(event_id)
    bookings = await get_bookings(callback_query.from_user.id)
    data = await state.get_data()
    if event_id in bookings:
        await callback_query.message.answer(text=i18n.t("text.already_booked"), reply_markup=kb.sub_default_btn)
    else:
        await book_event(callback_query.from_user.id, event_id, datetime.datetime.now(), slot_id)
        link = await get_link(event['start_datetime'], event['event_type'], event['id'], callback_query.from_user.id)
        # link = "Here will be link soon"
        club_name = await get_club_name(event['club'])
        await callback_query.message.answer(text="Ты записан на следующее мероприятие:\n" +
                                                 i18n.t("text.booked_event", event_name=event['name'],
                                                        club_name=club_name, event_type=event['event_type'],
                                                        start_time=event['start_datetime'].strftime(
                                                            '%d.%m.%y, %H:%M'),
                                                        duration=event['duration'], link=link),
                                            reply_markup=kb.sub_default_btn)


async def get_link(event_start_time, event_type, event_id, user_id):
    chat_id = await get_chatId(event_id)
    link = ''
    if event_type == 'Онлайн конференция' and event_start_time - datetime.datetime.now() > datetime.timedelta(minutes=5):
        link = "Ссылка появится за 5 минут до начала мероприятия!"
    elif event_type == "Видеочат":
        slot_time = await get_slot(user_id)
        if slot_time[0] - datetime.datetime.now() > datetime.timedelta(minutes=0):
            link = f"Ссылка появится в {slot_time[0].strftime('%H:%M')}"
        else:
            link = give_link_to_invite(chat_id, user_id)
    else:
        link = give_link_to_invite(chat_id, user_id)
    return link

