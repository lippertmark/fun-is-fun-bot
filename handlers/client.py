import i18n
from load import dp, bot
from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import keybords as kb


i18n.load_path.append('.')
i18n.set('locale', 'ru')

isSub = 0


@dp.message_handler(Text(equals="123"), state='*')
async def secret(message: types.Message, state: FSMContext):
    global isSub
    await message.answer("Поздравляю, теперь у тебя есть подписка", reply_markup=kb.sub_default_btn)
    async with state.proxy() as data:
        data['club'] = 'все клубы'
    isSub = 1


@dp.message_handler(commands=['cancel'], state='*')
async def process_cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if isSub:
        await message.answer("Ты перешел в главное меню", reply_markup=kb.sub_default_btn)
    else:
        await message.answer("Ты перешел в главное меню", reply_markup=kb.default_btn)
    kb.team_page = 0
    kb.categ_page = 0
    if current_state is None:
        return
    await state.reset_state(with_data=False)


@dp.message_handler(Text(equals="Маркетплейс️", ignore_case=True))
async def market(message: types.Message):
    await message.answer("Тут маркетплейс я завез", reply_markup=kb.get_web_app())


@dp.message_handler(Text(equals="Мои подписки", ignore_case=True), lambda c: isSub)
async def my_subs(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(f"Ты подписан на {data['club']}", reply_markup=kb.cancel_button)


@dp.message_handler(Text(equals="Мои бронирования", ignore_case=True), lambda c: isSub)
async def my_subs(message: types.Message, state: FSMContext):
    await message.answer(f"Пока нет бронирований, я же их не написал даже", reply_markup=kb.cancel_button)


@dp.message_handler(Text(equals="Помощь", ignore_case=True), lambda c: isSub)
async def my_subs(message: types.Message, state: FSMContext):
    await message.answer("Бог поможет", reply_markup=kb.cancel_button)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(i18n.t('text.hello'), reply_markup=kb.default_btn)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(i18n.t('text.help'))





