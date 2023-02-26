from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import WEB_APP_BASE
from typing import List, Tuple, Union

# resend verification code inline keyboard
resend_code_btn = InlineKeyboardButton("новый код", callback_data="new_code_request")
change_email_btn = InlineKeyboardButton("изменить email", callback_data="change_email")
resend_code_kb = InlineKeyboardMarkup().add(resend_code_btn).add(change_email_btn)

# main menu
create_activity_btn = KeyboardButton("Создать активность")
help_btn = KeyboardButton("Помощь")
current_activities_btn = KeyboardButton("Текущие активности")
statistics_btn = KeyboardButton("Статистика")
shop_btn = KeyboardButton("Магазин")
menu_kb = ReplyKeyboardMarkup([[create_activity_btn],
                               [help_btn],
                               [current_activities_btn],
                               [statistics_btn],
                               [shop_btn]], resize_keyboard=True)

# create activity menu
videochat_btn = KeyboardButton(text="Видеочат",
                               web_app=WebAppInfo(url=WEB_APP_BASE + '/videochat'))
online_conference_btn = KeyboardButton(text="Онлайн конференция",
                                       web_app=WebAppInfo(url=WEB_APP_BASE + '/conference'))
offline_event_btn = KeyboardButton(text="Оффлайн мероприятие",
                                   web_app=WebAppInfo(url=WEB_APP_BASE + '/offline_event'))
create_activity_menu_kb = ReplyKeyboardMarkup(keyboard=[[videochat_btn],
                                                        [online_conference_btn],
                                                        [offline_event_btn],
                                                        [KeyboardButton(text="Назад")]], resize_keyboard=True)


def create_save_event_kb(event_id):
    """
    Creates inline button to save event with save_event- + event_id as callback data.

    :param event_id:
    :return:
    """
    save_event_btn = InlineKeyboardButton(text="Да, сохранить",
                                          callback_data="save_event-"+event_id)
    return InlineKeyboardMarkup(inline_keyboard=[[save_event_btn]])


def create_booking_kb(event_id):
    """
    Creates inline registration button for client with book_event- + event_id as callback_data

    :param event_id:
    :return:
    """
    book_event_btn = InlineKeyboardButton(text="Зарегистрироваться",
                                          callback_data="book_event-"+event_id)
    return InlineKeyboardMarkup(inline_keyboard=[[book_event_btn]])


# delete event
delete_event_btn = InlineKeyboardButton(text="Удалить", callback_data="delete_event_request")
cancel_event_delete_btn = InlineKeyboardButton(text="Назад", callback_data="return")
delete_event_kb = InlineKeyboardMarkup(inline_keyboard=[[delete_event_btn, cancel_event_delete_btn]])

# confirmation of delete
no_delete_event_btn = InlineKeyboardButton(text="Отмена", callback_data="delete_event_cancel")
yes_delete_event_btn = InlineKeyboardButton(text="Да", callback_data="delete_event_confirmation")
yes_no_delete_event_kb = InlineKeyboardMarkup(inline_keyboard=[[no_delete_event_btn, yes_delete_event_btn]])

# shop control
add_item = InlineKeyboardButton(text="Добавить товар",
                                web_app=WebAppInfo(url=WEB_APP_BASE + '/shop/add_item'))
show_orders = InlineKeyboardButton(text="Список заказов",
                                   web_app=WebAppInfo(url=WEB_APP_BASE + '/shop/orders'))
shop_control_kb = InlineKeyboardMarkup(inline_keyboard=[[add_item], [show_orders]])

# temporary statistics
open_statistics_btn = InlineKeyboardButton(text="Открыть статистику канала",
                                           web_app=WebAppInfo(url="https://combot.org/c/1785291662/a"))
statistics_kb = InlineKeyboardMarkup(inline_keyboard=[[open_statistics_btn]])


async def build_inline_keyboard(items: List[Tuple[str, Union[int, str]]], page: int = 1, items_on_page=10):
    """
    Creates n-th page of dynamic keyboard for list of items.
    If n-th page does not exist - returns empty keyboard.

    :param items: list of tuples that represent button (text, callback data)
    :param page: page number
    :param items_on_page:
    :return:
    """
    kb = InlineKeyboardMarkup(row_width=3)
    total_pages = (len(items) + 9) // items_on_page

    if total_pages == 0:
        # nothing to show
        kb.row(InlineKeyboardButton(text="~пусто~", callback_data="empty"),
               InlineKeyboardButton(text="назад", callback_data="return"))
        return kb

    if page < 1 or page > total_pages:
        # page number out of bounds
        return kb

    # items on page
    start_id = (page - 1) * items_on_page
    end_id = min((total_pages - 1) * items_on_page + len(items) - start_id, page * items_on_page)
    for i in range(start_id, end_id):
        kb.row(InlineKeyboardButton(text=items[i][0], callback_data=items[i][1]), )

    # last row for navigation
    nav_row = [InlineKeyboardButton(text="Назад", callback_data="return")]
    if total_pages > 1:
        if page > 1:
            nav_row.append(InlineKeyboardButton(text="<", callback_data="previous_page"))
        if page < total_pages:
            nav_row.append(InlineKeyboardButton(text=">", callback_data="next_page"))
    kb.row(*nav_row)

    return kb


async def save_new_kb_info(state: FSMContext, items: List[Tuple[str, Union[int, str]]]):
    """
    Adds information about freshly created dynamic keyboard into user data storage.

    :param state:
    :param items:
    :return:
    """
    kb_info = (items, 1)  # (keyboard[(btn_text, callback_data)], page_number)
    user_data = await state.get_data()
    if user_data.get('kbs') is None:
        keyboards = []
    else:
        keyboards = user_data.get('kbs')
    keyboards.append(kb_info)
    await state.update_data(kbs=keyboards)
