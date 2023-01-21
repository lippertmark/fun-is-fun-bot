from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
webapp = WebAppInfo(url="https://eclectic-melba-d24886.netlify.app/")
hockey_teams = ["Ак барс", "Чеза", "Не шарю за хоккей", "но тут еще", 'Много команд']
inline_hockey = InlineKeyboardButton('Хоккей', callback_data='hockey')
inline_football = InlineKeyboardButton('Футбол', callback_data='football')
inline_basketball = InlineKeyboardButton('Баскетбол', callback_data='basketball')
inline_base = InlineKeyboardButton('Базовый', callback_data='base')
inline_stand = InlineKeyboardButton('Стандарт', callback_data='standard')
inline_prem = InlineKeyboardButton('Премиум', callback_data='premium')
inl_get_sub = InlineKeyboardButton('Стать членом сообщества', callback_data='buy_sub')
inl_buy = InlineKeyboardButton('Оплатить', callback_data='buy')
inl_store = InlineKeyboardButton(text="Store", web_app=webapp)
inl_menu = InlineKeyboardButton('Перейти в меню', callback_data='menu')
inl_back = InlineKeyboardButton('Назад', callback_data='back')
cancel_kb = KeyboardButton('/cancel')
find_club = KeyboardButton('Найти клуб️')
market = KeyboardButton('Маркетплейс️')

inline_categories = InlineKeyboardMarkup().row(inline_hockey, inline_football, inline_basketball)
cancel_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cancel_kb)
back_btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('Назад'))
default_btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(find_club).add(market)
club_btn = InlineKeyboardMarkup().add(inl_get_sub).add(inl_store).add(inl_menu)
buy_btn = InlineKeyboardMarkup().add(inl_buy)

subs_btn = InlineKeyboardMarkup().row(inline_base, inline_stand, inline_prem).add(inl_back)
all_teams_btn = InlineKeyboardMarkup()

for team in hockey_teams:
    all_teams_btn.add(InlineKeyboardButton(f"{team}", callback_data=team))
all_teams_btn.add(InlineKeyboardButton('Назад', callback_data='back'))


def get_web_app():
    keyboard = InlineKeyboardMarkup(row_width=1)
    one_butt = InlineKeyboardButton(text="Тестовая страница", web_app=webapp)
    keyboard.add(one_butt)
    return keyboard
