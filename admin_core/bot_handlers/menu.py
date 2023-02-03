from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from admin_core.chat_cleanup import clear_block, clear_io, add_trace, add_block_and_trace
from admin_core.customers import get_event_participants
from admin_core.admin_states import FSMAdminMenu
from admin_core import keyboards as k
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, and_
from db.models import Event, BookingEvent
from datetime import datetime, timedelta
import i18n

"""
Main admin menu
"""

i18n.load_path.append('./admin_core')
i18n.set('locale', 'ru')


async def show_menu(message: Message, state: FSMContext):
    """
    Removes all unnecessary data, puts user into main_menu state, and prints menu.

    :param message:
    :param state:
    :return:
    """
    await clear_io(message.from_user.id, state, message.bot)
    await state.reset_data()
    await state.set_state(FSMAdminMenu.main_menu.state)
    await message.answer(i18n.t('text.menu'), reply_markup=k.menu_kb)


# -------
# create activity section
async def create_activity_menu(message: Message, state: FSMContext):
    """
    Displays menu for creating new activity.

    :param message:
    :param state:
    :return:
    """
    await clear_io(message.from_user.id, state, message.bot)
    await state.reset_data()
    await add_trace(message.message_id, state)
    m = await message.answer(i18n.t('text.choose'), reply_markup=k.create_activity_menu_kb)
    await add_trace(m.message_id, state)


# -------
# help section
async def show_help(message: Message, state: FSMContext):
    """
    Displays main help info.

    :param message:
    :param state:
    :return:
    """
    await clear_io(message.from_user.id, state, message.bot)
    await state.reset_data()
    await add_trace(message.message_id, state)
    m = await message.answer(i18n.t('text.help'), reply_markup=k.call_support_kb)
    await add_trace(m.message_id, state)


async def show_support_contact(call: CallbackQuery, state: FSMContext):
    """
    Displays live support contact by request.

    :param call:
    :param state:
    :return:
    """
    await call.answer()
    m = await call.message.answer(i18n.t('text.call_help'))
    await add_trace(m.message_id, state)


# -------
# show events section
async def show_event_dates(message: Message, sm: sessionmaker, state: FSMContext):
    """
    First step in "show open events" process.
    Finds all possible dates and presents them as interactive keyboard.

    :param message:
    :param sm:
    :param state:
    :return:
    """
    await clear_io(message.from_user.id, state, message.bot)
    await state.reset_data()
    await add_trace(message.message_id, state)

    async with sm() as session:
        async with session.begin():
            dates_req = select(Event.start_datetime) \
                .where(Event.created_id == message.from_user.id) \
                .group_by(Event.start_datetime)\
                .order_by(Event.start_datetime.asc())
            event_dates = await session.execute(dates_req)

    available_dates = {date.start_datetime.date() for date in event_dates}  # set of available dates
    # forming kb
    dates_kb_info = []
    for date in available_dates:
        date_user = date.strftime("%d.%m")
        date_callback = date.strftime("oedates:%d.%m.%Y")  # oedates is unique identifier for this selection
        dates_kb_info.append((date_user, date_callback))

    await k.save_new_kb_info(state, dates_kb_info)
    m = await message.answer(i18n.t('text.choose'), reply_markup=await k.build_inline_keyboard(dates_kb_info))
    await add_trace(m.message_id, state)


async def show_open_events(call: CallbackQuery, sm: sessionmaker, state: FSMContext):
    """
    Finds all events for selected day and presents them as interactive keyboard.

    :param call:
    :param sm:
    :param state:
    :return:
    """
    selected_date = datetime.strptime(call.data, "oedates:%d.%m.%Y")

    # events for user on selected day
    async with sm() as session:
        async with session.begin():
            filtered_events_req = select(Event)\
                .where(and_(Event.created_id == call.from_user.id,
                            Event.start_datetime.between(
                                selected_date,
                                selected_date + timedelta(hours=23, minutes=59, seconds=59))))
            filtered_events = await session.execute(filtered_events_req)

    # forming kb
    events = [(f'{activity.Event.event_type}: {activity.Event.name}', f"oeid:{activity.Event.id}")
              for activity in filtered_events]  # oeid is unique identifier for this selection

    await call.answer()
    await k.save_new_kb_info(state, events)
    await call.message.edit_text(i18n.t('text.choose'), reply_markup=await k.build_inline_keyboard(events))


async def show_event_details(call: CallbackQuery, sm: sessionmaker, state: FSMContext):
    """
    Provides information about selected event.

    :param call:
    :param sm:
    :param state:
    :return:
    """
    q_id = int(call.data.split(':')[-1])  # id of selected event from callback data
    async with sm() as session:
        async with session.begin():
            event_data = await session.execute(select(Event).where(Event.id == q_id))
            event_data = event_data.one_or_none()
    await state.update_data(selected_event_id=event_data.Event.id, selected_event_name=event_data.Event.name)

    participants = await get_event_participants(event_data.Event.id, sm)

    event_info = f"{event_data.Event.event_type} {event_data.Event.name}\n" \
                 f"Начало: {event_data.Event.start_datetime.strftime('%d-%m-%Y %H:%M')}, продолжительность " \
                 f"{event_data.Event.duration // 3600} ч, {event_data.Event.duration % 3600 // 60} мин\n" \
                 f"Гостей: {len(participants)} / {event_data.Event.max_amount_of_people}\n"

    if event_data.Event.event_type == "Онлайн конференция" or event_data.Event.event_type == "Оффлайн мероприятие":
        event_info += f"Чат: {event_data.Event.telegram_group_invitation_link}"

    await call.answer()
    await k.save_new_kb_info(state, [('1', '1')])  # dummy kb to make "return" button work properly
    await call.message.edit_text(event_info, reply_markup=k.delete_event_kb)


async def request_event_delete(call: CallbackQuery, state: FSMContext):
    """
    Asks user to provide reason for deleting event.

    :param call:
    :param state:
    :return:
    """
    await call.answer()
    m = await call.message.answer(i18n.t('text.request_delete_reason'), reply_markup=ReplyKeyboardRemove())
    await add_block_and_trace(m.message_id, state)
    await state.set_state(FSMAdminMenu.delete_event_reason.state)


async def notification_event_delete(message: Message, state: FSMContext):
    """
    Asks user to confirm reason of event deletion.

    :param message:
    :param state:
    :return:
    """
    user_data = await state.get_data()
    confirm_msg = i18n.t('text.delete_confirmation') \
        .replace("X", user_data.get('selected_event_name')).replace("Y", message.text)
    await state.update_data(delete_event_reason=message.text)
    m = await message.answer(confirm_msg, reply_markup=k.yes_no_delete_event_kb)
    await add_trace(message.message_id, state)
    await add_trace(m.message_id, state)


async def confirmed_delete_event(call: CallbackQuery, sm: sessionmaker, state: FSMContext):
    """
    Executes event deletion: notifies all participants, deletes bookings and event itself.

    :param call:
    :param sm:
    :param state:
    :return:
    """
    await call.answer(i18n.t('text.deleted_successfully'), show_alert=True)
    user_data = await state.get_data()
    event = user_data.get("selected_event_id")
    msg = i18n.t('text.sorry_event_canceled')\
        .replace('X', user_data.get("selected_event_name"))\
        .replace('Y', user_data.get("delete_event_reason"))
    participants = await get_event_participants(event, sm)

    await state.set_state(FSMAdminMenu.main_menu.state)
    await clear_io(call.from_user.id, state, call.bot)
    await show_menu(call.message, state)

    async with sm() as session:
        async with session.begin():
            for participant in participants:
                participant_id = participant.UserClient.tg_id
                await call.bot.send_message(participant_id, msg)
                await session.execute(delete(BookingEvent).where(BookingEvent.user_id == participant_id))
            await session.execute(delete(Event).where(Event.id == event))


async def cancel_delete_event(call: CallbackQuery, state: FSMContext):
    """
    Rollback for event deletion.

    :param call:
    :param state:
    :return:
    """
    await clear_block(call.from_user.id, state, call.bot)
    await state.set_state(FSMAdminMenu.main_menu.state)


# -------
# statistics section
async def show_statistics(message: Message, state: FSMContext):
    """
    Displays statistics menu. TODO

    :param message:
    :param state:
    :return:
    """
    await clear_io(message.from_user.id, state, message.bot)
    await state.reset_data()
    await add_trace(message.message_id, state)
    m = await message.answer(i18n.t('text.show_statistics'))
    await add_trace(m.message_id, state)


# -------
# shop section
async def shop_control(message: Message, state: FSMContext):
    """
    Displays shop control buttons. TODO

    :param message:
    :param state:
    :return:
    """
    await clear_io(message.from_user.id, state, message.bot)
    await state.reset_data()
    await add_trace(message.message_id, state)
    m = await message.answer(i18n.t('text.shop_control'), reply_markup=k.shop_control_kb)
    await add_trace(m.message_id, state)


# -------
# handlers of kb navigation buttons
async def previous_page_kb(call: CallbackQuery, state: FSMContext):
    """
    Updates message with previous page of dynamic keyboard.

    :param call:
    :param state:
    :return:
    """
    await call.answer()
    user_data = await state.get_data()
    kb, page = user_data['kbs'][-1]

    await call.message.edit_text(text=i18n.t('text.choose'),
                                 reply_markup=await k.build_inline_keyboard(kb, page - 1))

    user_data['kbs'][-1] = (kb, page - 1)
    await state.update_data(user_data)


async def next_page_kb(call: CallbackQuery, state: FSMContext):
    """
    Updates message with next page of dynamic keyboard.

    :param call:
    :param state:
    :return:
    """
    await call.answer()
    user_data = await state.get_data()
    kb, page = user_data['kbs'][-1]

    await call.message.edit_text(text=i18n.t('text.choose'),
                                 reply_markup=await k.build_inline_keyboard(kb, page + 1))

    user_data['kbs'][-1] = (kb, page + 1)
    await state.update_data(user_data)


async def return_kb(call: CallbackQuery, state: FSMContext):
    """
    Updates message with previous step.

    :param call:
    :param state:
    :return:
    """
    user_data = await state.get_data()
    user_data['kbs'].pop(-1)

    if not user_data['kbs']:
        # return to main menu
        await clear_io(call.from_user.id, state, call.bot)
        await show_menu(call.message, state)
        await call.answer("вернулись в главное меню")
    else:
        # show previous step
        await call.answer("вернулись на предыдущий этап")
        kb, page = user_data['kbs'][-1]
        await call.message.edit_text(text=i18n.t('text.choose'),
                                     reply_markup=await k.build_inline_keyboard(kb, page))

    await state.update_data(user_data)


async def notify_empty_list(call: CallbackQuery):
    """
    Simple notification about empty list.

    :param call:
    :return:
    """
    await call.answer("совсем пусто")


def reg_menu_handlers(dp: Dispatcher):
    """
    Registers admin menu handlers in the dispatcher of the bot.

    :param dp: Dispatcher of the bot
    :return:
    """
    # -------
    # user requested menu
    dp.register_message_handler(show_menu, Text(equals="Меню", ignore_case=True), state=FSMAdminMenu.main_menu)

    # -------
    # create new event, entry button
    dp.register_message_handler(create_activity_menu, Text(equals="Создать активность", ignore_case=True),
                                state=FSMAdminMenu.main_menu)

    # -------
    # help
    dp.register_message_handler(show_help, Text(equals="Помощь", ignore_case=True), state=FSMAdminMenu.main_menu)
    # user requested live support
    dp.register_callback_query_handler(show_support_contact, text="call_help", state=FSMAdminMenu.main_menu)

    # -------
    # show active events process, entry button
    dp.register_message_handler(show_event_dates, Text(equals="Текущие активности", ignore_case=True),
                                state=FSMAdminMenu.main_menu)
    # choosing date of event
    dp.register_callback_query_handler(show_open_events, lambda c: c.data and c.data.startswith("oedates:"),
                                       state=FSMAdminMenu.main_menu)
    # choosing event
    dp.register_callback_query_handler(show_event_details, lambda c: c.data and c.data.startswith("oeid:"),
                                       state=FSMAdminMenu.main_menu)
    # user requested deletion of the event
    dp.register_callback_query_handler(request_event_delete, text="delete_event_request", state=FSMAdminMenu.main_menu)
    # user provided reason of deletion
    dp.register_message_handler(notification_event_delete, state=FSMAdminMenu.delete_event_reason)
    # user confirmed event_delete
    dp.register_callback_query_handler(confirmed_delete_event, text="delete_event_confirmation",
                                       state=FSMAdminMenu.delete_event_reason)
    # user canceled event_delete
    dp.register_callback_query_handler(cancel_delete_event, text="delete_event_cancel",
                                       state=FSMAdminMenu.delete_event_reason)

    # -------
    # statistics, entry button
    dp.register_message_handler(show_statistics, Text(equals="Статистика", ignore_case=True),
                                state=FSMAdminMenu.main_menu)

    # -------
    # shop, entry button
    dp.register_message_handler(shop_control, Text(equals="Магазин", ignore_case=True), state=FSMAdminMenu.main_menu)

    # -------
    # dynamic keyboard navigation
    dp.register_callback_query_handler(next_page_kb, text="next_page", state=FSMAdminMenu.main_menu)
    dp.register_callback_query_handler(previous_page_kb, text="previous_page", state=FSMAdminMenu.main_menu)
    dp.register_callback_query_handler(return_kb, text="return", state=FSMAdminMenu.main_menu)
    dp.register_callback_query_handler(notify_empty_list, text="empty", state=FSMAdminMenu.main_menu)
