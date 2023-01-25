from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardRemove

webapp = WebAppInfo(url="https://eclectic-melba-d24886.netlify.app/")

categories = ["Футбол", "Хоккей", "Баскетбол", "Шахматы", "Волейбол", "Бейсбол", "Гольф", "Теннис", "Спортивная мафия",
              "КС ГО", "Блогеры", "Настольный теннис", "Швеи", "клуб математиков"]
hockey_teams = ["Ак барс", "Чеза", "Салкын Чай", "Рубин", 'Спартак', 'Москва', 'Зенит', 'Ливерпуль', 'Ювентус',
                'Юрматы', 'Салават Юлаев', 'Манчестер', 'Бишекташ', 'Финербахче']


inline_base = InlineKeyboardButton('Базовый', callback_data='base')
inline_stand = InlineKeyboardButton('Стандарт', callback_data='standard')
inline_prem = InlineKeyboardButton('Премиум', callback_data='premium')
inl_get_sub = InlineKeyboardButton('Стать членом сообщества', callback_data='buy_sub')
inl_buy = InlineKeyboardButton('Оплатить', callback_data='buy')
inl_store = InlineKeyboardButton("Store", web_app=webapp)
inl_menu = InlineKeyboardButton('Перейти в меню', callback_data='menu')
inl_back = InlineKeyboardButton('Назад', callback_data='back')

find_club = KeyboardButton('Найти клуб️')
market = KeyboardButton('Маркетплейс️')


cancel_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('/cancel'))
back_btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('Назад'))
default_btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(find_club).add(market)


sub_default_btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton("Мои подписки"),
                                                                                        KeyboardButton("Мои бронирования"))\
    .add(find_club, market).add(KeyboardButton("Помощь"))
club_btn = InlineKeyboardMarkup().add(inl_get_sub).add(inl_store).add(inl_menu).add(inl_back)
buy_btn = InlineKeyboardMarkup().add(inl_buy)

subs_btn = InlineKeyboardMarkup().row(inline_base, inline_stand, inline_prem).add(inl_back)
categ_page = 0
team_page = 0
len_cat = len(categories)
len_team = len(hockey_teams)


def get_categories(str_):
    all_categories_btn = InlineKeyboardMarkup(row_width=2)
    global categ_page
    if str_ == '<' and categ_page >= 10:
        categ_page -= 10
    elif str_ == '>':
        categ_page += 10
    for i in range(len_cat - categ_page):
        all_categories_btn.row(InlineKeyboardButton(f"{categories[i + categ_page]}",
                                                    callback_data=categories[i + categ_page]))
        if i == 9:
            break
    if len(categories) > 10:
        all_categories_btn.add(InlineKeyboardButton("<", callback_data="<"),
                               InlineKeyboardButton(">", callback_data=">"))
    return all_categories_btn


def get_all_teams(str_):
    all_teams_btn = InlineKeyboardMarkup()
    global team_page
    if str_ == '<' and team_page >= 10:
        team_page -= 10
    elif str_ == '>':
        team_page += 10
    for i in range(len_team - team_page):
        all_teams_btn.add(InlineKeyboardButton(f"{hockey_teams[i + team_page]}",
                                               callback_data=hockey_teams[i + team_page]))
        if i == 9:
            break
    if len(hockey_teams) > 10:
        all_teams_btn.add(InlineKeyboardButton('Назад', callback_data='back'), InlineKeyboardButton("<", callback_data="<"),
                          InlineKeyboardButton(">", callback_data=">"))
    else:
        all_teams_btn.add(InlineKeyboardButton('Назад', callback_data='back'))
    return all_teams_btn


def get_web_app():
    keyboard = InlineKeyboardMarkup(row_width=1)
    one_butt = InlineKeyboardButton(text="Тестовая страница", web_app=webapp)
    keyboard.add(one_butt)
    return keyboard
