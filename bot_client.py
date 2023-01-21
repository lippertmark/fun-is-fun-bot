from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import keybords as k
from config import *
import i18n

i18n.load_path.append('.')
i18n.set('locale', 'ru')
storage = MemoryStorage()
bot = Bot(token=TOKEN_TELEGRAM)
dp = Dispatcher(bot=bot, storage=storage)


class ClientStates(StatesGroup):
    find_cl = State()
    club_info = State()
    club_page = State()
    buy_sub = State()


@dp.message_handler(commands=['cancel'], state='*')
async def process_cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer("Canceled", reply_markup=k.default_btn)
    if current_state is None:
        return
    await state.finish()


@dp.message_handler(Text(equals="Назад", ignore_case=True), state=ClientStates.find_cl)
async def back_func(message: types.Message, state: FSMContext):
    await process_cancel_command(message, state)


@dp.message_handler(Text(equals="Найти клуб️", ignore_case=True))
async def find_club(message: types.Message):
    await message.answer("(Напиши Ак барс!)", reply_markup=k.back_btn)
    await message.answer("Напиши название клуба либо выбери категорию из списка:",
                         reply_markup=k.inline_categories)
    await ClientStates.find_cl.set()


@dp.message_handler(Text(equals="Назад", ignore_case=True), state=ClientStates.club_info)
async def back_func(message: types.Message, state: FSMContext):
    await find_club(message)


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.club_info)
async def the_team(callback_query: types.CallbackQuery):
    code = callback_query.data
    print(code)
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        await callback_query.message.delete()
        await find_club(callback_query.message)
    else:
        await bot.edit_message_text(text=f"{code} is the best team ever",
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=k.club_btn)
        await ClientStates.club_page.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.club_page)
async def club_page(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'menu':
        await callback_query.message.delete()
        await process_cancel_command(callback_query.message, state)
    else:
        await bot.edit_message_text(text="Выберите подписку",
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=k.subs_btn)
        await ClientStates.buy_sub.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.buy_sub)
async def club_page(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        await callback_query.message.delete()
        await process_cancel_command(callback_query.message, state)
    elif code == 'standard':
        await bot.edit_message_text(text="Оплата на сумму 199 рублей, +тут же инфа о покупке",
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=k.buy_btn)
        await ClientStates.buy_sub.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.find_cl)
async def teams_list(callback_query: types.CallbackQuery):
    code = callback_query.data
    print(code)
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(text=f"Тут из БД вываливается список {code} команд",
                                chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                reply_markup=k.all_teams_btn)
    await ClientStates.club_info.set()


@dp.message_handler(Text(equals="Назад", ignore_case=True), state=ClientStates.club_info)
async def back_func(callback_query: types.CallbackQuery):
    await teams_list(callback_query)


@dp.message_handler(state=ClientStates.find_cl)
async def search(message: types.Message):
    if message.text == 'Ак барс':
        await message.answer("Ак барс чемпион!")
    else:
        await message.answer("Команда не найдена!")


@dp.message_handler(Text(equals="Маркетплейс️", ignore_case=True))
async def market(message: types.Message):
    await message.answer("Тут маркетплейс я завез", reply_markup=k.get_web_app())


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(i18n.t('text.hello'), reply_markup=k.default_btn)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(i18n.t('text.help'))


if __name__ == '__main__':
    executor.start_polling(dp)
