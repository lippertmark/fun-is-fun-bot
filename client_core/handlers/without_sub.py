import datetime

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import LabeledPrice, ContentType
from aiogram import types, Dispatcher
import i18n

from load import bot, PAYMENT_TOKEN
import client_core.keybords as kb
from db.utils import get_sport_types, get_clubs, get_club_info, get_subscribes, add_subscription
from client_core.handlers.support_func import delete_last_message, is_swipeable, delete_all_messages
from client_core.handlers.start import process_cancel_command
i18n.load_path.append('.')
i18n.set('locale', 'ru')


class ClientStates(StatesGroup):
    find_club = State()
    club_info = State()
    club_page = State()
    buy_sub = State()


async def find_club(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['msg'].append(message.message_id)
        msg = await message.answer(i18n.t("text.search_menu"), reply_markup=kb.cancel_button)
        data['msg'].append(msg.message_id)
        categories = await get_sport_types()
        if categories is False:
            msg = await message.answer(i18n.t("text.db_error"))
        else:
            msg = await message.answer(i18n.t("text.choose_category"),
                                       reply_markup=kb.get_all(categories, 0, is_back=False))
            data['category_page'] = 0
            data['msg'].append(msg.message_id)
    await ClientStates.find_club.set()


async def teams_list(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    categories = await get_sport_types()
    async with state.proxy() as data:
        if code == '<' or code == '>':
            if is_swipeable(code, data['category_page'], len(categories)):
                data['category_page'] = data['category_page'] + 1 if code == '>' else data['category_page'] - 1
                await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id,
                                                    reply_markup=kb.get_all(categories, data['category_page'],
                                                                            is_back=False))
        elif code == 'back':
            teams = await get_clubs(data['category'])
            msg = await bot.send_message(text=i18n.t("text.choose_club", category=categories[int(data['category'])]),
                                         chat_id=callback_query.from_user.id,
                                         reply_markup=kb.get_all(teams, 0, is_back=True))
            data['msg'].append(msg.message_id)
        else:
            data['category'] = code
            teams = await get_clubs(data['category'])
            await bot.edit_message_text(text=i18n.t("text.choose_club", category=categories[int(data['category'])]),
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.get_all(teams, 0, is_back=True))
        data['clubs_page'] = 0
    await ClientStates.club_info.set()


async def search(message: types.Message, state: FSMContext):
    club_info = await get_club_info(message.text)
    if club_info:
        async with state.proxy() as data:
            data["club"] = club_info['id']
            data["category"] = club_info['sport_type']
            await delete_last_message(message.from_user.id, state)
            data['msg'].pop()
            club = await get_club_info(data['club'])
            msg = await bot.send_photo(chat_id=message.from_user.id,
                                       photo=club['photo'], caption=club['description'],
                                       reply_markup=kb.club_btn)
            data['msg'].append(msg.message_id)
        await ClientStates.club_page.set()
    else:
        await message.answer(i18n.t("text.club_not_exist", club=message.text))


async def the_team(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        if code == 'back':
            categories = await get_sport_types()
            await bot.edit_message_text(text=i18n.t("text.choose_category"),
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=kb.get_all(categories, 0, is_back=False))
            await ClientStates.find_club.set()
            data['category_page'] = 0
        elif code == '<' or code == '>':
            clubs = await get_clubs(data['category'])
            if is_swipeable(code, data['clubs_page'], len(clubs)):
                data['clubs_page'] = data['clubs_page'] + 1 if code == '>' else data['clubs_page'] - 1
                await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                                    message_id=callback_query.message.message_id,
                                                    reply_markup=kb.get_all(clubs, data['clubs_page'],
                                                                            is_back=False))
        else:
            if code != 'back1':
                data["club"] = code
            await delete_last_message(callback_query.from_user.id, state)
            data['msg'].pop()
            club = await get_club_info(data['club'])
            msg = await bot.send_photo(chat_id=callback_query.from_user.id,
                                       photo=club['photo'], caption=club['description'],
                                       reply_markup=kb.club_btn)
            data['msg'].append(msg.message_id)
            await ClientStates.club_page.set()


async def club_page(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'menu':
        callback_query.message.from_user.id = callback_query.from_user.id
        return await process_cancel_command(callback_query.message, state)
    elif code == 'back':
        await delete_last_message(callback_query.from_user.id, state)
        async with state.proxy() as data:
            data['msg'].pop()
        await teams_list(callback_query, state)
    else:
        async with state.proxy() as data:
            club_info = await get_club_info(data['club'])
            await delete_last_message(callback_query.from_user.id, state)
            data['msg'].pop()
            msg = await bot.send_message(text=i18n.t('text.subscriptions', clubname=(club_info['name']),
                                                     base_price=club_info['base_subscription']['price'],
                                                     standard_price=club_info['standard_subscription']['price'],
                                                     premium_price=club_info['premium_subscription']['price']),
                                         chat_id=callback_query.from_user.id, parse_mode="Markdown",
                                         reply_markup=kb.subs_btn)
            data['msg'].append(msg.message_id)
        await ClientStates.buy_sub.set()


async def buy_sub(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if code == 'back':
        callback_query.data = 'back1'
        await the_team(callback_query, state)
    else:
        async with state.proxy() as data:
            club_info = await get_club_info(data['club'])
            data["subs"] = club_info[code]['id']
            data["sub_type"] = club_info[code]['type']
            subs = await get_subscribes(callback_query.from_user.id)
            if not int(data['club']) in (subs.keys()):
                await delete_last_message(callback_query.from_user.id, state)
                data['msg'].pop()
                msg = await bot.send_invoice(callback_query.from_user.id,
                                             title="Оплата подписки",
                                             description=i18n.t('text.payment', price=club_info[code]['price'],
                                                                sub_type=club_info[code]['type'],
                                                                club=club_info['name']),
                                             provider_token=PAYMENT_TOKEN,
                                             currency='rub',
                                             is_flexible=False,
                                             prices=[LabeledPrice(
                                                 label=f"{club_info['name']} - "
                                                       f"{club_info[code]['type']}",
                                                 amount=club_info[code]['price'] * 100)],
                                             start_parameter='subscription_payment',
                                             payload='subscription_payment')
                data['msg'].append(msg.message_id)
            else:
                await bot.edit_message_text(text=i18n.t("text.subscription_exist", club=club_info['name']),
                                            chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=kb.InlineKeyboardMarkup().add(kb.inl_back))


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def process_successful_payment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        club_info = await get_club_info(data['club'])
        await message.answer(
            text=i18n.t('text.congratulation', clubname=club_info['name']),
            reply_markup=kb.sub_default_btn)
        await delete_all_messages(message.from_user.id, state)
        data['msg'].clear()
        await add_subscription(message.from_user.id, data["sub_type"], int(data['club']), data["subs"], datetime.datetime.now())
    await state.reset_state(with_data=False)


def reg_without_sub_handlers(dp: Dispatcher):
    dp.register_message_handler(find_club, Text(equals="Найти клуб️", ignore_case=True))

    dp.register_callback_query_handler(teams_list, state=ClientStates.find_club)

    dp.register_message_handler(search, state=ClientStates.find_club)

    dp.register_callback_query_handler(the_team, state=ClientStates.club_info)

    dp.register_callback_query_handler(club_page, state=ClientStates.club_page)

    dp.register_callback_query_handler(buy_sub, state=ClientStates.buy_sub)

    dp.register_pre_checkout_query_handler(process_pre_checkout_query, lambda query: True, state=ClientStates.buy_sub)
    dp.register_message_handler(process_successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT,
                                state=ClientStates.buy_sub)
