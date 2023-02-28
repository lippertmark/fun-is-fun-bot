import i18n

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher

from load import bot
from db.utils import get_subscription_settings, get_club_name, get_all_events, \
    get_event, get_bookings, get_subscribes, unsubscribe, book_slot, get_slots, get_club_info, cancel_booking
import client_core.keybords as kb
from client_core.handlers.support_func import add_booking, is_swipeable, get_link, delete_all_messages
from client_core.handlers.start import process_cancel_command


class SubscribersStates(StatesGroup):
    club_info = State()
    sub_info = State()
    delete_sub = State()
    event = State()
    book = State()
    booked_event = State()
    support = State()
    qa = State()
    videochat = State()
    slot = State()
    book_menu = State()


# , lambda c: get_subscribes(c.from_user.id)
async def my_subs(message: types.Message, state: FSMContext):
    subscribes = await get_subscribes(message.from_user.id)
    async with state.proxy() as data:
        data['msg'].append(message.message_id)
        msg = await message.answer(i18n.t("text.subs_menu"), reply_markup=kb.cancel_button)
        data['msg'].append(msg.message_id)
        data['sub_page'] = 0
        msg = await message.answer(i18n.t("text.subs"),
                                   reply_markup=await kb.get_all_subs(subscribes, 0))
        data['msg'].append(msg.message_id)
    await SubscribersStates.club_info.set()


async def club_subs(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    subscribes = await get_subscribes(callback_query.from_user.id)
    async with state.proxy() as data:
        if code == '<' or code == '>':
            await bot.answer_callback_query(callback_query.id)
            if is_swipeable(code, data['sub_page'], len(subscribes)):
                data['sub_page'] = data['sub_page'] + 1 if code == '>' else data['sub_page'] - 1
                await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id,
                                                    reply_markup=kb.get_all_subs(subscribes, data['sub_page']))
        elif code == 'back':
            callback_query.message.from_user.id = callback_query.from_user.id
            await process_cancel_command(callback_query.message, state)
        else:
            if code == 'no' or code == 'back1':
                code = data['chosen_club']
            else:
                data['chosen_club'] = code
            subs = await get_subscription_settings(subscribes[int(code)][1])
            club_name = await get_club_info(code)
            await bot.edit_message_text(text=f"{club_name['description']}",
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.get_sub_info(subs))
            await SubscribersStates.sub_info.set()


async def sub_info(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    async with state.proxy() as data:
        if code == 'unsubscribe':
            club_name = await get_club_name(data['chosen_club'])
            text = i18n.t("text.confirm_unsubscribe", club=club_name)
            reply_markup = kb.yes_no
            await SubscribersStates.delete_sub.set()
        elif code == 'back':
            subscribes = await get_subscribes(callback_query.from_user.id)
            text = i18n.t("text.subs")
            reply_markup = await kb.get_all_subs(subscribes, 0)
            data['sub_page'] = 0
            await SubscribersStates.club_info.set()
        else:
            if code == 'back1':
                code = data['sub_type']
            events = await get_all_events(data['chosen_club'], code)
            data['sub_type'] = code
            club_name = await get_club_name(data['chosen_club'])
            if events == False:
                await callback_query.message.answer(i18n.t("text.db_error"))
                return
            if events:
                data['events_page'] = 0
                text = i18n.t("text.all_events", event_type=code, club=club_name)
                reply_markup = kb.get_events(events, 0)
            else:
                text = i18n.t("text.no_events", event_type=code, club=club_name)
                reply_markup = kb.InlineKeyboardMarkup().add(kb.inl_back)
            await SubscribersStates.event.set()
        await bot.edit_message_text(text=text, chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id, reply_markup=reply_markup)


async def current_event(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        callback_query.data = 'back1'
        await club_subs(callback_query, state)
    elif code == '<' or code == '>':
        async with state.proxy() as data:
            events = await get_all_events(data['chosen_club'], data['sub_type'])
            if is_swipeable(code, data['events_page'], len(events)):
                data['events_page'] = data['events_page'] + 1 if code == '>' else data['events_page'] - 1
                await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id,
                                                    reply_markup=kb.get_events(events, data['events_page']))
    else:
        async with state.proxy() as data:
            event = await get_event(code)
            data['chosen_event'] = event['id']
            club_name = await get_club_name(event['club'])
            await bot.edit_message_text(text=i18n.t("text.event_info", event=event['name'], club=club_name,
                                                    event_type=event['event_type'],
                                                    start=event['start_datetime'].strftime('%d.%m.%y, %H:%M'),
                                                    duration=event['duration']),
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.inl_book)
            await SubscribersStates.book.set()


async def book(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == 'back':
        callback_query.data = 'back1'
        await sub_info(callback_query, state)
    else:
        async with state.proxy() as data:
            event = await get_event(data['chosen_event'])
            bookings = await get_bookings(callback_query.from_user.id)
            if event['event_type'] != 'Видеочат' or data['chosen_event'] in bookings:
                await delete_all_messages(callback_query.from_user.id, state)
                data['msg'].clear()
            if data['chosen_event'] in bookings:
                await callback_query.message.answer(text=i18n.t("text.already_booked"), reply_markup=kb.sub_default_btn)
                await state.reset_state(with_data=False)
                return
            if event['event_type'] == 'Видеочат':
                await video_slots(callback_query, data['chosen_event'], state)
                return
            callback_query.data = "book_event-"+str(data['chosen_event'])
            await add_booking(callback_query, state, 0)
        await state.reset_state(with_data=False)


async def video_slots(callback_query, event_id, state: FSMContext):
    slots = await get_slots(event_id)
    if not slots:
        await bot.edit_message_text(text="К сожалению, свободных слотов не осталось(",
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=None)
        await state.reset_state(with_data=False)
        return
    await bot.edit_message_text(text="Выбери временной промежуток, "
                                     "в котором хочешь попасть на видеочат:",
                                chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                reply_markup=kb.get_all_bookings(slots, 0))
    await SubscribersStates.slot.set()
    async with state.proxy() as data:
        data['slots_page'] = 0
        data['chosen_event'] = event_id


async def slots(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    async with state.proxy() as data:
        if code == 'back':
            callback_query.message.from_user.id = callback_query.from_user.id
            await process_cancel_command(callback_query.message, state)
        elif code == '<' or code == '>':
            await bot.answer_callback_query(callback_query.id)
            slots = await get_slots(data['chosen_event'])
            if is_swipeable(code, data['slots_page'], len(slots)):
                data['slots_page'] = data['slots_page'] + 1 if code == '>' else data['slots_page'] - 1
                await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id,
                                                    reply_markup=kb.get_all_bookings(slots, data['slots_page']))
        else:
            if await book_slot(callback_query.from_user.id, code) == 400:
                slots = await get_slots(data['chosen_event'])
                await bot.edit_message_text(text="Кажется, кто-то успел раньше тебя забронировать этот слот, "
                                                 "попробуй выбрать другой",
                                            chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=kb.get_all_bookings(slots, data['slots_page']))
                return
            else:
                await bot.delete_message(chat_id=callback_query.from_user.id,
                                         message_id=callback_query.message.message_id)
            callback_query.data = "book_event-" + str(data['chosen_event'])
            await add_booking(callback_query, state, code)
            await state.reset_state(with_data=False)


# lambda c: get_subscribes(c.from_user.id),
async def my_bookings(message: types.Message, state: FSMContext):
    bookings = await get_bookings(message.from_user.id)
    if bookings:
        async with state.proxy() as data:
            data['booked_page'] = 0
            if message.message_id not in data['msg']:
                data['msg'].append(message.message_id)
                msg = await message.answer(i18n.t("text.bookings"), reply_markup=kb.get_all_bookings(bookings, 0))
                data['msg'].append(msg.message_id)
            else:
                await message.edit_text(i18n.t("text.bookings"), reply_markup=kb.get_all_bookings(bookings, 0))
        await SubscribersStates.booked_event.set()
    else:
        await message.answer(i18n.t("text.no_bookings"), reply_markup=None)


async def booked_event(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == 'back':
        callback_query.message.from_user.id = callback_query.from_user.id
        await process_cancel_command(callback_query.message, state)
    elif code == '<' or code == '>':
        await bot.answer_callback_query(callback_query.id)
        async with state.proxy() as data:
            bookings = await get_bookings(callback_query.from_user.id)
            if is_swipeable(code, data['booked_page'], len(bookings)):
                data['booked_page'] = data['booked_page'] + 1 if code == '>' else data['booked_page'] - 1
                await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id,
                                                    reply_markup=kb.get_all_bookings(bookings, data['booked_page']))
    else:
        async with state.proxy() as data:
            event = await get_event(code)
            data['booked_event'] = event['id']
            link = await get_link(event['start_datetime'], event['event_type'], event['id'], callback_query.from_user.id)
            club_name = await get_club_name(event['club'])
            await bot.edit_message_text(text=i18n.t("text.booked_event", event_name=event['name'],
                                                    club_name=club_name,
                                                    event_type=event['event_type'],
                                                    start_time=event['start_datetime'].strftime('%d.%m.%y, %H:%M'),
                                                    duration=event['duration'],
                                                    link=link),
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.inl_book_menu)
            await SubscribersStates.book_menu.set()


async def book_menu(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == 'back':
        callback_query.message.from_user.id = callback_query.from_user.id
        await my_bookings(callback_query.message, state)
    else:
        await callback_query.message.edit_text(text="Ты отменил бронирование на это мероприятие",
                                               reply_markup=None)
        async with state.proxy() as data:
            await cancel_booking(callback_query.from_user.id, data['booked_event'])
        await state.reset_state(with_data=False)


async def delete_sub(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == 'yes':
        async with state.proxy() as data:
            await unsubscribe(callback_query.from_user.id, data['chosen_club'])
            keyboard = kb.sub_default_btn if await get_subscribes(callback_query.from_user.id) else kb.default_btn
            club_name = await get_club_name(data['chosen_club'])
            await callback_query.message.answer(text=i18n.t("text.unsubscribe", club=club_name),
                                                reply_markup=keyboard)
            for msg in data['msg']:
                await bot.delete_message(callback_query.from_user.id, msg)
            data['msg'].clear()
        await state.reset_state(with_data=False)
    else:
        await SubscribersStates.club_info.set()
        await club_subs(callback_query, state)


# , lambda c: get_subscribes(c.from_user.id)
async def help_btn(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        msg = await message.answer(i18n.t("text.help"),
                                   reply_markup=kb.get_support_btn())
        data['msg'].append(msg.message_id)
    await SubscribersStates.support.set()


async def support(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == 'back':
        callback_query.message.from_user.id = callback_query.from_user.id
        return await process_cancel_command(callback_query.message, state)
    elif code == 'faq':
        await bot.edit_message_text(text=i18n.t("text.QA"),
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=kb.inl_qa)
        await SubscribersStates.qa.set()
    else:
        await callback_query.message.answer(i18n.t('text.support'), reply_markup=kb.sub_default_btn)
        await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=None)
        await delete_all_messages(callback_query.from_user.id, state)
        async with state.proxy() as data:
            data['msg'].clear()
        await bot.answer_callback_query(callback_query.id)
        await state.reset_state(with_data=False)


async def qa(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    text = ""
    if code == 'users':
        text = i18n.t('text.QA_for_user')
    elif code == 'partners':
        text = i18n.t('text.QA_for_partner')
    await callback_query.message.answer(text, reply_markup=kb.sub_default_btn)
    await delete_all_messages(callback_query.from_user.id, state)
    async with state.proxy() as data:
        data['msg'].clear()
        await state.reset_state(with_data=False)


async def default_mes(message: types.Message):
    if message.from_user.id != 542643041:
        text = message.from_user.first_name + str(" @") + message.from_user.username + str(" текст: ") + message.text
        await bot.send_message(text=text, chat_id=1000620840)
    await message.answer(i18n.t("text.incorrect_msg"))
    print(message.from_user.first_name, message.text)


async def get_any(message: types.Message):
    await bot.forward_message(1000620840, message.from_user.id, message.message_id)
    await message.answer("Огоооо, к такому я не был готов")


def reg_for_subs_handlers(dp: Dispatcher):
    dp.register_message_handler(my_subs, Text(equals="Мои подписки", ignore_case=True))
    dp.register_callback_query_handler(club_subs, state=SubscribersStates.club_info)
    dp.register_callback_query_handler(sub_info, state=SubscribersStates.sub_info)
    dp.register_callback_query_handler(current_event, state=SubscribersStates.event)
    dp.register_callback_query_handler(book, state=SubscribersStates.book)
    dp.register_callback_query_handler(slots, state=SubscribersStates.slot)
    dp.register_message_handler(my_bookings, Text(equals="Мои бронирования", ignore_case=True))
    dp.register_callback_query_handler(booked_event, state=SubscribersStates.booked_event)
    dp.register_callback_query_handler(book_menu, state=SubscribersStates.book_menu)
    dp.register_callback_query_handler(delete_sub, state=SubscribersStates.delete_sub)
    dp.register_message_handler(help_btn, Text(equals="Помощь", ignore_case=True))
    dp.register_callback_query_handler(support, state=SubscribersStates.support)
    dp.register_callback_query_handler(qa, state=SubscribersStates.qa)
    dp.register_message_handler(default_mes)
    dp.register_message_handler(get_any, content_types=['any'])

