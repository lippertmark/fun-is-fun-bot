from aiogram import types, Dispatcher
from aiogram.dispatcher.dispatcher import FSMContext

from client_core.handlers.support_func import add_booking
from db.utils import get_event
from client_core.handlers.for_subscribers import video_slots
from client_core.handlers.support_func import delete_all_messages


async def book_from_notif(callback_query: types.CallbackQuery, state: FSMContext):
    event_id = int(callback_query.data.split('-')[1])
    event = await get_event(event_id)
    if event['event_type'] == 'Видеочат':
        await video_slots(callback_query, event['id'], state)
        await delete_all_messages(callback_query.from_user.id, state)
        async with state.proxy() as data:
            data['msg'].clear()
        return
    await add_booking(callback_query, state, 0)
    await callback_query.message.delete()


def reg_notif_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(book_from_notif, lambda c: c.data and 'book_event' in c.data, state='*')

