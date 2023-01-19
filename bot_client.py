from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import keybords as k
import re
from config import *
import i18n

i18n.load_path.append('.')
i18n.set('locale', 'ru')

storage = MemoryStorage()
bot = Bot(token=TOKEN_TELEGRAM)
dp = Dispatcher(bot=bot, storage=storage)


class ClientStates(StatesGroup):
    tel_num = State()
    email = State()


async def get_num(message: types.Message):
    await ClientStates.tel_num.set()
    await message.answer(i18n.t('text.tel_num'), reply_markup=k.markup_request)


@dp.message_handler(commands=['cancel'], state='*')
async def process_cancel_command(message: types.Message, state: FSMContext):
    print(message.text)
    current_state = await state.get_state()
    await message.reply("Canceled", reply_markup=types.ReplyKeyboardRemove())
    if current_state is None:
        return
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'reg')
async def process_callback_button1(callback_query: types.CallbackQuery):
    print(callback_query.message.text)
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    await get_num(callback_query.message)


@dp.message_handler(lambda message: message, content_types=types.ContentType.CONTACT, state=ClientStates.tel_num)
async def check_correct_photo(message: types.Message):
    print(message.text)
    await ClientStates.next()
    await message.reply("А теперь пришли почту")


@dp.message_handler(content_types=types.ContentType.ANY, state=ClientStates.tel_num)
async def check_photo(message: types.Message):
    print(message.text)
    if types.ContentType.TEXT == message.content_type:
        if re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
                    message.text):
            await ClientStates.next()
            await message.reply("А теперь пришли почту")
        else:
            return await message.reply("Пришли контакт")


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    print(message.text)
    await message.answer(i18n.t('text.hello'), reply_markup=k.inline_kb1)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    print(message.text)
    await message.reply(i18n.t('text.help'))


if __name__ == '__main__':
    executor.start_polling(dp)
