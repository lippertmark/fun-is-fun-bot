import os

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, Bot

from admin_core.chat_cleanup import clear_block, clear_io, add_trace, add_block_and_trace, delete_msg
from admin_core.customers import get_event_participants, get_affiliated_club, get_subscribers_tg_id
from admin_core.admin_states import FSMAdminMenu
from admin_core import event_maker as em
from admin_core import keyboards as k

from sqlalchemy import select, delete, and_, cast, Date
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

from db.models import Event, BookingEvent, UserAdmin, SportClub
from event_module import give_link_to_invite
from datetime import datetime, timedelta
import json
import i18n


dotenv_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
TOKEN_TELEGRAM_CLIENT = os.getenv("TOKEN_TELEGRAM_CLIENT")
"""
Main admin menu
"""

i18n.load_path.append('./admin_core')
i18n.set('locale', 'ru')

client_bot = Bot(TOKEN_TELEGRAM_CLIENT)


async def show_menu(message: Message, sm: sessionmaker, state: FSMContext):
    """
    Removes all unnecessary data, puts user into main_menu state, and prints menu.

    :param message:
    :param sm:
    :param state:
    :return: id of menu message
    """
    # checking if user already registered
    async with sm() as session:
        async with session.begin():
            # select users with sender id
            user = await session.execute((select(UserAdmin.tg_id).where(UserAdmin.tg_id == message.chat.id)))
            user = user.one_or_none()
    if user is None:
        await message.answer(i18n.t('text.unauthorised'))
        return

    await clear_io(message.from_user.id, state, message.bot)
    await state.reset_data()
    await state.set_state(FSMAdminMenu.main_menu.state)
    m = await message.answer(i18n.t('text.menu'), reply_markup=k.menu_kb)
    await state.update_data(menu_msg=m.message_id)  # to delete it when needed
    return m.message_id


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
    await add_trace(message.message_id, state)
    m = await message.answer(i18n.t('text.choose'), reply_markup=k.create_activity_menu_kb)
    await add_trace(m.message_id, state)


# handler for data from webapp
async def handle_webapp_data(web_app_message, state: FSMContext):
    """
    Handler for data from event_creation WebApp.

    :param web_app_message:
    :param state:
    :return:
    """
    data = json.loads(web_app_message.web_app_data.data)

    event_type = web_app_message.web_app_data.button_text
    event_at_date_time = data.get('datetime').split('T')

    if event_type == "Видеочат":
        message = f"Вы создаёте видеочат\n" \
                  f"Название: {data.get('name')}\n" \
                  f"Проведёт: {data.get('organizer', web_app_message.from_user.username)}\n" \
                  f"Дата: {event_at_date_time[0]}\n" \
                  f"Начало в: {event_at_date_time[1]}\n" \
                  f"Продлится: {data.get('duration')} минут\n" \
                  f"Из них на каждого гостя: {data['durationForOne']} минут\n" \
                  f"Всё верно?"
    elif event_type == "Онлайн конференция":
        message = f"Вы создаёте онлайн конференцию\n" \
                  f"Название: {data.get('name')}\n" \
                  f"Проведёт: {data.get('organizer', web_app_message.from_user.username)}\n" \
                  f"Дата: {event_at_date_time[0]}\n" \
                  f"Начало в: {event_at_date_time[1]}\n" \
                  f"Продлится: {data.get('duration')} минут\n" \
                  f"Максимум гостей: {data.get('max_persons')}\n" \
                  f"Всё верно?"
    else:
        message = f"Вы создаёте оффлайн мероприятие\n" \
                  f"Название: {data.get('name')}\n" \
                  f"Проведёт: {data.get('organizer', web_app_message.from_user.username).strip('@')}\n" \
                  f"Дата: {event_at_date_time[0]}\n" \
                  f"Начало в: {event_at_date_time[1]}\n" \
                  f"Продлится: {data.get('duration')} минут\n" \
                  f"Максимум гостей: {data.get('max_persons')}\n" \
                  f"Всё верно?"

    save_data = {"event_type": event_type, "event_data": data}

    unique_data_id = str(datetime.now())
    await state.update_data({f"save_event-{unique_data_id}": save_data})

    m = await web_app_message.answer(message, reply_markup=k.create_save_event_kb(unique_data_id))
    await add_trace(m.message_id, state)


async def confirm_event_creation(call: CallbackQuery, sm: sessionmaker, state: FSMContext):
    user_data = await state.get_data()
    saved_data = user_data.get(call.data)
    user_data.update({call.data: {}})

    event_type = saved_data.get("event_type").lower()
    event_data = saved_data.get("event_data")

    if event_type == "видеочат":
        event_id = await em.new_videoconference(sm,
                                                event_data.get('organizer', call.from_user.username),
                                                event_data.get('name'),
                                                datetime.strptime(event_data.get('datetime'), "%Y-%m-%dT%H:%M"),
                                                int(event_data.get('duration', 0)),
                                                int(event_data.get('durationForOne', 0)),
                                                call.from_user.id)
    elif event_type == "онлайн конференция":
        event_id = await em.new_online_conference(sm,
                                                  event_data.get('organizer', call.from_user.username),
                                                  event_data.get('name'),
                                                  datetime.strptime(event_data.get('datetime'), "%Y-%m-%dT%H:%M"),
                                                  int(event_data.get('duration', 0)),
                                                  int(event_data.get('max_persons', 0)),
                                                  call.from_user.id)
    else:
        event_id = await em.new_offline_event(sm, event_data.get('organizer', call.from_user.username),
                                              event_data.get('name'),
                                              datetime.strptime(event_data.get('datetime'), "%Y-%m-%dT%H:%M"),
                                              int(event_data.get('duration', 0)),
                                              int(event_data.get('max_persons', 0)),
                                              call.from_user.id)

    await call.answer("Событие добавлено", show_alert=True)
    await call.message.delete()

    # section for sending notifications to subscribers
    club_id = await get_affiliated_club(sm, call.from_user.id)
    # selecting club name
    async with sm() as session:
        async with session.begin():
            q = select(SportClub.name).where(SportClub.id == club_id)
            club = await session.execute(q)
            club = club.one_or_none()

    event_at_date_time = event_data.get('datetime').split('T')
    msg = f"Привет!\n" \
          f"В твоей подписке на клуб {club.name} новое мероприятие:\n" \
          f"{event_data.get('name')} ({event_type}), состоится {event_at_date_time[0]} в {event_at_date_time[1]} " \
          f"и продлится {int(event_data.get('duration')) // 60} ч {int(event_data.get('duration')) % 60} мин"
    kb = k.create_booking_kb(event_id)
    subscribers = await get_subscribers_tg_id(event_type, club_id, sm)
    for subscriber in subscribers:
        await client_bot.send_message(subscriber, msg, reply_markup=kb)


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
    await add_trace(message.message_id, state)
    m = await message.answer(i18n.t('text.help'))
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
    await add_trace(message.message_id, state)

    async with sm() as session:
        async with session.begin():
            dates_req = select(Event.start_datetime) \
                .where(and_(Event.created_id == message.from_user.id,
                            Event.start_datetime > datetime.now() - timedelta(minutes=10)))
            event_dates = await session.execute(dates_req)

    # list of unique available dates
    available_dates = list({date.start_datetime.date() for date in event_dates})
    available_dates.sort()
    available_dates = [date.strftime('%d.%m.%Y') for date in available_dates]

    # oedates is unique identifier for this selection
    dates_kb_info = [(date, 'oedates:' + date) for date in available_dates]

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
    selected_date = datetime.strptime(call.data, "oedates:%d.%m.%Y").date()

    # events for user on selected day
    async with sm() as session:
        async with session.begin():
            filtered_events_req = select(Event) \
                .where(and_(Event.created_id == call.from_user.id,
                            cast(Event.start_datetime, Date) == selected_date,
                            Event.start_datetime > (datetime.now() - timedelta(minutes=10)))) \
                .order_by(Event.start_datetime.asc())
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
                 f"Проведёт: {event_data.Event.tg_alias}\n" \
                 f"Начало: {event_data.Event.start_datetime.strftime('%d-%m-%Y %H:%M')}\n" \
                 f"Продолжительность: {event_data.Event.duration // 60} ч, {event_data.Event.duration % 60} мин\n" \
                 f"Гостей: {len(participants)} / {event_data.Event.max_amount_of_people}\n"

    if event_data.Event.event_type == "Онлайн конференция" or event_data.Event.event_type == "Оффлайн мероприятие":
        try:
            chat_link = give_link_to_invite(event_data.Event.telegram_group_id, call.from_user.id)
        except:
            chat_link = "не удалось получить ссылку на приглашение в чат"
        event_info += f"Чат (ссылка действует 5 минут): {chat_link}"

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
    msg = i18n.t('text.sorry_event_canceled') \
        .replace('X', user_data.get("selected_event_name")) \
        .replace('Y', user_data.get("delete_event_reason"))
    participants = await get_event_participants(event, sm)

    await state.set_state(FSMAdminMenu.main_menu.state)
    # to resend with new menu_kb later
    await delete_msg(call.from_user.id, user_data.get("menu_msg"), call.bot)
    await clear_io(call.from_user.id, state, call.bot)
    await show_menu(call.message, sm, state)

    async with sm() as session:
        async with session.begin():
            for participant in participants:
                participant_id = participant.UserClient.tg_id
                try:  # to avoid errors when user blocked us
                    await client_bot.send_message(participant_id, msg)
                except:
                    pass
                await session.execute(delete(BookingEvent).where(and_(BookingEvent.user_id == participant_id,
                                                                      BookingEvent.event_id == event)))
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
    Displays statistics menu.

    :param message:
    :param state:
    :return:
    """
    await clear_io(message.from_user.id, state, message.bot)
    await add_trace(message.message_id, state)
    m = await message.answer(i18n.t('text.choose'), reply_markup=k.statistics_kb)
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


async def return_kb(call: CallbackQuery, sm: sessionmaker, state: FSMContext):
    """
    Updates message with previous step.

    :param call:
    :param sm:
    :param state:
    :return:
    """
    user_data = await state.get_data()
    user_data['kbs'].pop(-1)
    await state.update_data(user_data)

    if not user_data['kbs']:
        # return to main menu
        await delete_msg(call.from_user.id, user_data.get("menu_msg"), call.bot)  # to resend with new menu_kb later
        await clear_io(call.from_user.id, state, call.bot)
        m_id = await show_menu(call.message, sm, state)
        await state.update_data(menu_msg=m_id)
        await call.answer("вернулись в главное меню")
    else:
        # show previous step
        await call.answer("вернулись на предыдущий этап")
        kb, page = user_data['kbs'][-1]
        await call.message.edit_text(text=i18n.t('text.choose'),
                                     reply_markup=await k.build_inline_keyboard(kb, page))


async def notify_empty_list(call: CallbackQuery):
    """
    Simple notification about empty list.

    :param call:
    :return:
    """
    await call.answer("совсем пусто")


async def return_to_menu_kb_btn(message: Message, sm: sessionmaker, state: FSMContext):
    """
    Another kb button to return to menu.

    :param message:
    :param sm:
    :param state:
    :return:
    """
    user_data = await state.get_data()
    await add_trace(message.message_id, state)
    await delete_msg(message.from_user.id, user_data.get("menu_msg"), message.bot)  # to resend with new menu_kb later
    await clear_io(message.from_user.id, state, message.bot)
    m_id = await show_menu(message, sm, state)
    await state.update_data(menu_msg=m_id)


def reg_menu_handlers(dp: Dispatcher):
    """
    Registers admin menu handlers in the dispatcher of the bot.

    :param dp: Dispatcher of the bot
    :return:
    """
    # -------
    # user requested menu
    dp.register_message_handler(show_menu, Text(equals="Меню", ignore_case=True), state="*")
    dp.register_message_handler(show_menu, commands=['menu'], state="*")

    # -------
    # create new event, entry button
    dp.register_message_handler(create_activity_menu, Text(equals="Создать активность", ignore_case=True),
                                state=FSMAdminMenu.main_menu)
    # handle new event data from WebApp
    dp.register_message_handler(handle_webapp_data, content_types="web_app_data", state=FSMAdminMenu.main_menu)
    # confirm new event and add to db
    dp.register_callback_query_handler(confirm_event_creation, lambda c: c.data and c.data.startswith("save_event"),
                                       state=FSMAdminMenu.main_menu)

    # -------
    # help
    dp.register_message_handler(show_help, Text(equals="Помощь", ignore_case=True), state=FSMAdminMenu.main_menu)

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

    # -------
    # another implementation of "return to menu" btn
    dp.register_message_handler(return_to_menu_kb_btn, Text(equals="назад", ignore_case=True),
                                state=FSMAdminMenu.main_menu)
