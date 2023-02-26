import i18n
from load import dp, bot
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import client_core.keybords as kb
import datetime
from db.utils import create_client_user, is_user, get_subscribes, get_subscription_settings
from client_core.handlers.support_func import delete_all_messages, add_booking
i18n.load_path.append('client_core/.')
i18n.set('locale', 'ru')


@dp.message_handler(Text(equals="Главное меню"), state='*')
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


@dp.message_handler(commands=['start'], state="*")
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


@dp.message_handler(Text(equals="Маркетплейс️", ignore_case=True))
async def market(message: types.Message):
    await message.answer("Маркетплейс:", reply_markup=kb.get_web_app())


@dp.callback_query_handler(lambda c: c.data and 'book_event' in c.data)
async def book_from_notif(callback_query: types.CallbackQuery, state: FSMContext):
    print("IN START:", callback_query.data)
    await add_booking(callback_query, state, 0)
    callback_query.data = callback_query.data.split('-')[1]
    await callback_query.message.delete()


dp.register_message_handler(process_cancel_command, commands=['menu'], state='*')
