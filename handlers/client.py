import i18n
from load import dp, bot
from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import keybords as kb
import datetime
from db_client.utils import create_client_user, get_subscribes, is_user

i18n.load_path.append('.')
i18n.set('locale', 'ru')


@dp.message_handler(Text(equals="Главное меню"), state='*')
async def process_cancel_command(message: types.Message, state: FSMContext):
    """
    Drop all states and delete useless messages and return to main menu
    """
    current_state = await state.get_state()
    async with state.proxy() as data:
        data['teams_page'], data['category_page'], data['sub_page'], data['events_page'] = 0, 0, 0, 0
        try:
            if message.text == 'Главное меню':
                await message.delete()
            for msg in data['msg']:
                print('im trying to delete', msg.text)
                await msg.delete()
                print('deleted succesfully')
        finally:
            data['msg'].clear()
            keyboard = kb.sub_default_btn if get_subscribes(message.from_user.id) else kb.default_btn
            data['msg'].append(await message.answer(i18n.t('text.menu'), reply_markup=keyboard))
            if current_state is not None:
                await state.reset_state(with_data=False)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    if message.from_user.id != 542643041:
        await bot.send_message(text=f"на старт нажал @{message.from_user.username}",
                               chat_id=1000620840)
    async with state.proxy() as data:
        data['msg'] = []
    if not is_user(message.from_user.id):
        create_client_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                           message.from_user.username, datetime.datetime.now(), 'started')
    keyboard = kb.sub_default_btn if get_subscribes(message.from_user.id) else kb.default_btn
    await message.answer(i18n.t('text.hello', name=message.from_user.first_name), reply_markup=keyboard)


@dp.message_handler(Text(equals="Маркетплейс️", ignore_case=True))
async def market(message: types.Message):
    await message.answer("Маркетплейс:", reply_markup=kb.get_web_app())


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(i18n.t('text.help'))
