from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from config import *
import i18n

i18n.load_path.append('.')
i18n.set('locale', 'ru')


bot = Bot(token=TOKEN_TELEGRAM)
dp = Dispatcher(bot)


inline_btn_1 = InlineKeyboardButton('Регистрация!', callback_data='reg')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)

markup_request = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton('Отправить свой контакт ☎️', request_contact=True)
)


async def get_num(message: types.Message):
    msg = await message.answer(i18n.t('text.tel_num'), reply_markup=markup_request)


@dp.callback_query_handler(lambda c: c.data == 'reg')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    await get_num(callback_query.message)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(i18n.t('text.hello'), reply_markup=inline_kb1)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(i18n.t('text.help'))


if __name__ == '__main__':
    executor.start_polling(dp)
