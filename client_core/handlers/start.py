import i18n
from load import bot
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import client_core.keybords as kb
import datetime
from db.utils import create_client_user, is_user, get_subscribes
from client_core.handlers.support_func import delete_all_messages
i18n.load_path.append('client_core/.')
i18n.set('locale', 'ru')


async def process_cancel_command(message: types.Message, state: FSMContext):
    """
    Drop all states and delete useless messages and return to main menu
    """
    current_state = await state.get_state()
    async with state.proxy() as data:
        data['teams_page'], data['category_page'], data['sub_page'], data['events_page'] = 0, 0, 0, 0
        if message.text == 'Главное меню':
            await message.delete()
        await delete_all_messages(message.from_user.id, state)
        data['msg'].clear()
        keyboard = kb.sub_default_btn if await get_subscribes(message.from_user.id) else kb.default_btn
        msg = await message.answer(i18n.t('text.menu'), reply_markup=keyboard)
        data['msg'].append(msg.message_id)
        if current_state is not None:
            await state.reset_state(with_data=False)


async def process_start_command(message: types.Message, state: FSMContext):
    if message.from_user.id != 542643041:
        await bot.send_message(text=f"на старт нажал @{message.from_user.username}",
                               chat_id=1000620840)
    if await is_user(message.from_user.id) is None:
        await create_client_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                                 message.from_user.username, datetime.datetime.now())
    subs = await get_subscribes(message.from_user.id)
    if subs is False:
        await message.answer("На сервере ведутся тех.работы")
    keyboard = kb.sub_default_btn if subs else kb.default_btn
    await message.answer(i18n.t('text.hello', name=message.from_user.first_name), reply_markup=keyboard)
    await state.reset_state(with_data=False)
    await state.update_data(msg=[])


async def market(message: types.Message):
    await message.answer("Маркетплейс:", reply_markup=kb.get_web_app())


def reg_default_handlers(dp: Dispatcher):
    dp.register_message_handler(process_cancel_command, Text(equals="Главное меню"), state='*')
    dp.register_message_handler(process_cancel_command, commands=['menu'], state='*')
    dp.register_message_handler(process_start_command, commands=['start'], state='*')
    dp.register_message_handler(market, Text(equals="Маркетплейс️", ignore_case=True))
