from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

inline_btn_1 = InlineKeyboardButton('Регистрация!', callback_data='reg')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
cancel_kb = KeyboardButton('/cancel')
tel_kb = KeyboardButton('Отправить свой контакт ☎️', request_contact=True)


markup_request = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    tel_kb).add(cancel_kb)


#
# from aiogram.types import ReplyKeyboardRemove, \
#     ReplyKeyboardMarkup, KeyboardButton, \
#     InlineKeyboardMarkup, InlineKeyboardButton
#
# inline_btn_1 = InlineKeyboardButton('Регистрация!', callback_data='reg')
# inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
#
# cancel_kb = KeyboardButton('/cancel')
# find_club = KeyboardButton('Найти клуб️')
# market = KeyboardButton('Маркетплейс️')
#
# cancel_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(cancel_kb)
#
