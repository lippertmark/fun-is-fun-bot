from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardRemove
from db_client.utils import get_club_name, get_subscription_settings, get_event, get_absolutely_all_events


webapp = WebAppInfo(url="https://sage-mermaid-396618.netlify.app")

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
buy_btn = InlineKeyboardMarkup().add(inl_buy)
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


def get_all(list_, is_back):
    """
    :param list_: list of clubs or categories
    :param is_back: is need to add 'back' button?
    :return: Inline keyboard with list, max 10 line
    """
    inl_kb = InlineKeyboardMarkup()
    for i in range(len(list_)):
        inl_kb.row(InlineKeyboardButton(f"{list_[i][1]}",
                                        callback_data=list_[i][0]))
        if i == 9:
            break
    if len(list_) > 10:
        if is_back:
            add_buttons(inl_kb, len(list_))
        else:
            inl_kb.add(InlineKeyboardButton("<", callback_data="<"),
                       InlineKeyboardButton(">", callback_data=">"))
    else:
        if is_back:
            inl_kb.add(InlineKeyboardButton('Назад', callback_data='back'))
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


def get_all_subs(subs, page):
    inl_kb = InlineKeyboardMarkup()
    page = page * 10
    count = 0
    for sub in subs:
        if count >= page:
            inl_kb.row(InlineKeyboardButton(f"{get_club_name(sub)} "
                                            f"- {get_subscription_settings(subs[sub])['subscription_type']}",
                                            callback_data=sub))
        count += 1
        if count == page + 9:
            break
    add_buttons(inl_kb, len(subs))
    return inl_kb


def get_all_bookings(bookings, page):
    inl_kb = InlineKeyboardMarkup()
    page *= 10
    count = 0
    all_events = get_absolutely_all_events()
    for booking in bookings:
        if count >= page:
            inl_kb.row(InlineKeyboardButton(f"{all_events[booking]['name']} от {get_club_name(all_events[booking]['club'])}",
                                            callback_data=booking))
        count += 1
        if count == 9 + page:
            break
    add_buttons(inl_kb, len(bookings))
    return inl_kb


def swipe(list_, page, is_back):
    inl_kb = InlineKeyboardMarkup()
    for i in range(len(list_) - page * 10):
        inl_kb.add(InlineKeyboardButton(f"{list_[i + page * 10][1]}", callback_data=list_[i + page * 10][0]))
        if i == 9:
            break
    if is_back:
        add_buttons(inl_kb, 12)
    else:
        inl_kb.add(InlineKeyboardButton("<", callback_data="<"),
                   InlineKeyboardButton(">", callback_data=">"))
    return inl_kb


def get_support_btn():
    inl_support = InlineKeyboardMarkup()
    inl_support.add(InlineKeyboardButton("Поддержка", callback_data='support'),
                    InlineKeyboardButton("Часто задаваемые вопросы", callback_data='faq')).add(inl_back)
    return inl_support


def get_sub_info(sub):
    subs = get_subscription_settings(sub)
    tarif = InlineKeyboardMarkup()
    for i in subs['includes']:
        tarif.add(InlineKeyboardButton(i, callback_data=i))
    tarif.add(inl_store, InlineKeyboardButton("Отменить подписку", callback_data="unsubscribe")).add(inl_back)
    return tarif


def get_web_app():
    keyboard = InlineKeyboardMarkup(row_width=1)
    one_butt = InlineKeyboardButton(text="Тестовая страница", web_app=webapp)
    keyboard.add(one_butt)
    return keyboard

