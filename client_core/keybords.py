from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardRemove
from db.utils import get_club_name, get_subscription_settings

webapp = WebAppInfo(url="https://eclectic-melba-d24886.netlify.app")

# Here is simple inline buttons
inl_base = InlineKeyboardButton('Базовый', callback_data='base_subscription')
inl_stand = InlineKeyboardButton('Стандарт', callback_data='standard_subscription')
inl_prem = InlineKeyboardButton('Премиум', callback_data='premium_subscription')
inl_get_sub = InlineKeyboardButton('Стать членом сообщества', callback_data='buy_sub')
inl_buy = InlineKeyboardButton('Оплатить', callback_data='buy')
inl_store = InlineKeyboardButton("Store", web_app=webapp)
inl_menu = InlineKeyboardButton('Перейти в меню', callback_data='menu')
inl_back = InlineKeyboardButton('Назад', callback_data='back')

# Here is simple reply Keyboard buttons
find_club_btn = KeyboardButton('Найти клуб️')
market_btn = KeyboardButton('Маркетплейс️')
my_subs_btn = KeyboardButton("Мои подписки")
my_books_btn = KeyboardButton("Мои бронирования")


# Here is ReplyKeyboards
cancel_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('Главное меню'))
default_btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(find_club_btn).add(market_btn)
sub_default_btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).\
    add(my_subs_btn, my_books_btn).add(find_club_btn, market_btn).add(KeyboardButton("Помощь"))

# Here is InlineKeyboards
club_btn = InlineKeyboardMarkup().add(inl_get_sub).add(inl_store).add(inl_menu).add(inl_back)
buy_btn = InlineKeyboardMarkup().add(inl_buy).add(inl_back)
subs_btn = InlineKeyboardMarkup().row(inl_base, inl_stand, inl_prem).add(inl_back)
yes_no = InlineKeyboardMarkup().add(InlineKeyboardButton("Да", callback_data='yes')). \
    add(InlineKeyboardButton("нет", callback_data='no'))
inl_book = InlineKeyboardMarkup().add(InlineKeyboardButton("Забронировать", callback_data='book')).add(inl_back)
inl_qa = InlineKeyboardMarkup().add(InlineKeyboardButton("Для пользователей", callback_data='users'))\
    .add(InlineKeyboardButton("Для партнеров", callback_data='partners'))


def add_buttons(kb, length):
    # Add '<', '>' and 'back' buttons where using swipes
    if length > 9:
        kb.add(InlineKeyboardButton('Назад', callback_data='back'),
               InlineKeyboardButton("<", callback_data="<"),
               InlineKeyboardButton(">", callback_data=">"))
    else:
        kb.add(InlineKeyboardButton('Назад', callback_data='back'))


def get_all(items, page, is_back):
    """
    :param items: list of clubs or categories
    :param is_back: is need to add 'back' button?
    :param page: page num
    :return: Inline keyboard with list, max 10 line
    """
    inl_kb = InlineKeyboardMarkup()
    page *= 10
    count = 0
    for item in items:
        if count >= page:
            inl_kb.row(InlineKeyboardButton(f"{items[item]}",
                                            callback_data=item))
        count += 1
        if count == page + 9:
            break
    if len(items) > 10:
        if is_back:
            add_buttons(inl_kb, len(items))
        else:
            inl_kb.add(InlineKeyboardButton("<", callback_data="<"),
                       InlineKeyboardButton(">", callback_data=">"))
    else:
        if is_back:
            inl_kb.add(InlineKeyboardButton('Назад', callback_data='back'))
    return inl_kb


async def get_all_subs(subs, page):
    inl_kb = InlineKeyboardMarkup()
    page = page * 10
    count = 0
    for sub in subs:
        if count >= page:
            inl_kb.row(InlineKeyboardButton(f"{await get_club_name(sub)} "
                                            f"- {subs[sub][0]}",
                                            callback_data=sub))
        count += 1
        if count == page + 9:
            break
    add_buttons(inl_kb, len(subs))
    return inl_kb


def get_sub_info(subs):
    inl_kb = InlineKeyboardMarkup()
    for i in subs['includes']:
        inl_kb.add(InlineKeyboardButton(i, callback_data=i))
    inl_kb.add(inl_store, InlineKeyboardButton("Отменить подписку", callback_data="unsubscribe")).add(inl_back)
    return inl_kb


def get_events(events, page):
    inl_event = InlineKeyboardMarkup()
    page = page * 10
    count = 0
    for event in events:
        if count >= page:
            inl_event.add(InlineKeyboardButton(f"{events[event]['name']}", callback_data=events[event]['id']))
        count += 1
        if count == page + 9:
            break
    add_buttons(inl_event, len(events))
    return inl_event


def get_all_bookings(bookings, page):
    inl_booking = InlineKeyboardMarkup()
    page *= 10
    count = 0
    for booking in bookings:
        if count >= page:
            inl_booking.add(InlineKeyboardButton(f"{bookings[booking][0]} - {bookings[booking][1]}",
                                                 callback_data=str(booking)))
        count += 1
        if count == page + 10:
            break
    add_buttons(inl_booking, len(bookings))
    return inl_booking


def get_support_btn():
    inl_support = InlineKeyboardMarkup()
    inl_support.add(InlineKeyboardButton("Поддержка", callback_data='support'),
                    InlineKeyboardButton("Часто задаваемые вопросы", callback_data='faq')).add(inl_back)
    return inl_support


def get_web_app():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton(text="Тестовая страница", web_app=webapp)
    keyboard.add(button).add(KeyboardButton('Главное меню'))
    return keyboard
