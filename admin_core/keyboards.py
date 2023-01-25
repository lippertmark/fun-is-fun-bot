from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# resend verification code inline keyboard
resend_code_btn = InlineKeyboardButton("новый код", callback_data="new_code_request")
change_email_btn = InlineKeyboardButton("изменить email", callback_data="change_email")
resend_code_keyboard = InlineKeyboardMarkup().add(resend_code_btn).add(change_email_btn)
