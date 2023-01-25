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


class ClientStates(StatesGroup):
    find_cl = State()
    club_info = State()
    club_page = State()
    buy_sub = State()
    succesfully_paid = State()


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


@dp.message_handler(Text(equals="Найти клуб️", ignore_case=True))
async def find_club(message: types.Message):
    msg = await message.answer("Это костыльное сообщение, чтобы inline & reply kb не ругались",
                               reply_markup=kb.cancel_button)
    # await msg.delete()
    await message.answer("Напиши название клуба либо выбери категорию из списка:",
                         reply_markup=kb.get_categories('1'))
    await ClientStates.find_cl.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.find_cl)
async def teams_list(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == '<' or code == '>':
        if (kb.categ_page != 0 and code == '<') or (code == '>' and (kb.len_cat - kb.categ_page) >= 10):
            await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                message_id=callback_query.message.message_id,
                                                reply_markup=kb.get_categories(code))
        return
    async with state.proxy() as data:
        if code != 'back':
            data['category'] = code
        else:
            code = data['category']
    await bot.edit_message_text(text=f"Тут из БД вываливается список {code} команд",
                                chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                reply_markup=kb.get_all_teams(code))
    await ClientStates.club_info.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.club_info)
async def the_team(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == '<' or code == '>':
        if (kb.team_page != 0 and code == '<') or (code == '>' and (kb.len_team - kb.team_page) >= 10):
            await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                message_id=callback_query.message.message_id,
                                                reply_markup=kb.get_all_teams(code))
        return
    async with state.proxy() as data:
        if code != 'back1':
            data['team'] = code
        else:
            code = data['team']
    if code == 'back':
        kb.team_page = 0
        await callback_query.message.delete()
        await find_club(callback_query.message)
    else:
        await bot.edit_message_text(text=f"{code} is the best team ever",
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=kb.club_btn)
        async with state.proxy() as data:
            data["club"] = code
        await ClientStates.club_page.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.club_page)
async def club_page(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'menu':
        await callback_query.message.delete()
        await process_cancel_command(callback_query.message, state)
    elif code == 'back':
        callback_query.data = 'back'
        await teams_list(callback_query, state)
    else:
        await bot.edit_message_text(text="Выберите подписку",
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=kb.subs_btn)
        await ClientStates.buy_sub.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.buy_sub)
async def buy_sub(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        callback_query.data = 'back1'
        await the_team(callback_query, state)
    elif code == 'standard' or code == 'base' or code == 'premium':
        async with state.proxy() as data:
            await bot.edit_message_text(text=f"Оплата на сумму 199 рублей, подписка на {data['club']}, тариф {code}",
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.buy_btn)
        async with state.proxy() as data:
            data["subs"] = code
        await ClientStates.succesfully_paid.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.succesfully_paid)
async def send_subs(callback_query: types.CallbackQuery, state: FSMContext):
    global isSub
    await bot.edit_message_text(text="Ура ты дошел до конца",
                                chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                reply_markup=None)
    async with state.proxy() as data:
        await callback_query.message.answer(text=f"У тебя появился доступ к всему функционалу, потому что ты купил "
                                                 f"{data['subs']} подписку на {data['club']}, {data['category']}",
                                            reply_markup=kb.sub_default_btn)
    isSub = 1
    await state.reset_state(with_data=False)


@dp.message_handler(state=ClientStates.find_cl)
async def search(message: types.Message):
    if message.text == 'Ак барс':
        await message.answer(text=f"{message.text} is the best team ever", reply_markup=kb.club_btn)
        await ClientStates.club_page.set()
    else:
        await message.answer("Команда не найдена!")


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


@dp.message_handler(state='*')
async def default_mes(message: types.Message):
    await message.answer("Я ниче не понял, давай без сообщений пока, если у тебя все плохо, пиши /cancel")


