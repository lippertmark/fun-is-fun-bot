from aiogram.types import LabeledPrice, ContentType

from load import dp, bot, PAYMENT_TOKEN
import i18n
import datetime
from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from . import client
from handlers.additional_funcs import *
from db_client.utils import *
from aiogram.dispatcher.filters import Text

i18n.load_path.append('.')
i18n.set('locale', 'ru')


class ClientStates(StatesGroup):
    find_cl = State()
    club_info = State()
    club_page = State()
    buy_sub = State()
    successfully_paid = State()
    club_sub = State()
    in_sub = State()
    delete_sub = State()
    support = State()
    event = State()
    book = State()
    booked = State()
    booked_event = State()
    qa = State()


@dp.message_handler(Text(equals="Найти клуб️", ignore_case=True))
async def find_club(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['msg'].append(message)
        data['msg'].append(await message.answer("Ты перешел в меню поиска команды! Можешь воспользоваться "
                                                "поиском или выбрать подходящую категорию",
                                                reply_markup=kb.cancel_button))
        categories = all_sport_types()
        data['msg'].append(await message.answer("Напиши название клуба либо выбери категорию из списка:",
                                                reply_markup=kb.get_all(categories, is_back=False)))
        data['category_page'] = 0
        # data['category'] = ''
    await ClientStates.find_cl.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.find_cl)
async def teams_list(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        if code == '<' or code == '>':
            page = data['category_page']
            categories = all_sport_types()
            data['category_page'] = await swipe(code, callback_query, page, categories, is_back=False)
            return
        elif code == 'back':
            teams = get_list_of_sport_clubes_by_type(data['category'])
            data['msg'].append(await bot.send_message(text=f'''Вот команды из категории "{get_category_name(data['category'])}"''',
                                   chat_id=callback_query.from_user.id,
                                   reply_markup=kb.get_all(teams, is_back=True)))
        else:
            data['category'] = code
            teams = get_list_of_sport_clubes_by_type(data['category'])
            await bot.edit_message_text(text=f'''Вот команды из категории "{get_category_name(data['category'])}"''',
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.get_all(teams, is_back=True))
        data['teams_page'] = 0
    await ClientStates.club_info.set()


@dp.message_handler(state=ClientStates.find_cl)
async def search(message: types.Message, state: FSMContext):
    club_info = get_club_info(message.text)
    if club_info:
        async with state.proxy() as data:
            data["club"] = club_info['id']
            data["category"] = club_info['sport_type']
            await delete_last_message(state)
            data['msg'].pop()
            club = get_club_info(data['club'])
            msg = await bot.send_photo(chat_id=message.from_user.id,
                                       photo=club['photo'], caption=club['description'],
                                       reply_markup=kb.club_btn)
            data['msg'].append(msg)
        await ClientStates.club_page.set()
    else:
        await message.answer(f'Я не смог найти команду "{message.text}", '
                             f'убедись, что ты написал название правильно, или '
                             f'попробуй найти команду из списка')


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.club_info)
async def the_team(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        if code == 'back':
            categories = all_sport_types()
            await bot.edit_message_text(text="Напиши название клуба либо выбери категорию из списка:",
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.get_all(categories, is_back=False))
            await ClientStates.find_cl.set()
            data['category_page'] = 0
        elif code == '<' or code == '>':
            teams = get_list_of_sport_clubes_by_type(data['category'])
            page = data['teams_page']
            data['teams_page'] = await swipe(code, callback_query, page, teams, is_back=True)
        else:
            if code != 'back1':
                data["club"] = code
            await delete_last_message(state)
            data['msg'].pop()
            club = get_club_info(data['club'])
            msg = await bot.send_photo(chat_id=callback_query.from_user.id,
                                       photo=club['photo'], caption=club['description'],
                                       reply_markup=kb.club_btn)
            data['msg'].append(msg)
            await ClientStates.club_page.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.club_page)
async def club_page(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'menu':
        callback_query.message.from_user.id = callback_query.from_user.id
        return await client.process_cancel_command(callback_query.message, state)
    elif code == 'back':
        await delete_last_message(state)
        async with state.proxy() as data:
            data['msg'].pop()
        await teams_list(callback_query, state)
    else:
        async with state.proxy() as data:
            club_info = get_club_info(data['club'])
            await delete_last_message(state)
            data['msg'].pop()
            msg = await bot.send_message(text=i18n.t('text.subscriptions', clubname=(club_info['name']),
                                                     base_price=club_info['base_subscription']['price'],
                                                     standard_price=club_info['standard_subscription']['price'],
                                                     premium_price=club_info['premium_subscription']['price']),
                                         chat_id=callback_query.from_user.id, parse_mode="Markdown",
                                         reply_markup=kb.subs_btn)
            data['msg'].append(msg)
        await ClientStates.buy_sub.set()


@dp.callback_query_handler(lambda c: c.data, state=ClientStates.buy_sub)
async def buy_sub(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        callback_query.data = 'back1'
        await the_team(callback_query, state)
    else:
        async with state.proxy() as data:
            club_info = get_club_info(data['club'])
            data["subs"] = club_info[code]['id']
            data['sub_name'] = club_info[code]['subscription_type']
            if not int(data['club']) in get_subscribes(callback_query.from_user.id).keys():
                await bot.send_invoice(callback_query.from_user.id,
                                       title="Оплата подписки",
                                       description=f"Подписка {get_club_name(data['club'])} - "
                                                   f"{club_info[code]['subscription_type']} - на месяц",
                                       provider_token=PAYMENT_TOKEN,
                                       currency='rub',
                                       is_flexible=False,
                                       prices=[LabeledPrice(
                                           label=f"{get_club_name(data['club'])} - "
                                                 f"{club_info[code]['subscription_type']}",
                                           amount=club_info[code]['price'])],
                                       start_parameter='subscription_payment',
                                       payload='subscription_payment')
            else:
                await bot.edit_message_text(text=f"У тебя уже есть подписка на "
                                                 f"{get_club_name(data['club'])}, ты не можешь купить ее повторно",
                                            chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=kb.InlineKeyboardMarkup().add(kb.inl_back))


@dp.pre_checkout_query_handler(lambda query: True, state=ClientStates.buy_sub)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state=ClientStates.buy_sub)
async def process_successful_payment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        await message.answer(
            text=i18n.t('text.congratulation', clubname=get_club_name(data['club'])),
            reply_markup=kb.sub_default_btn)
        for msg in data['msg']:
            await msg.delete()
        data['msg'].clear()
        add_subscription(message.from_user.id, data["subs"], data['club'])
    await state.reset_state(with_data=False)
