from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from admin_core.admin_states import FSMRegistration, FSMAdminMenu
from admin_core.mailer import send_code, TIME_FORMAT
from admin_core import keyboards as k
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from db.models import UserAdmin
from datetime import datetime
import i18n

"""
Full user registration process
"""

i18n.load_path.append('./admin_core')
i18n.set('locale', 'ru')


async def greet(message: Message, sm: sessionmaker, state: FSMContext) -> None:
    """
    First message.
    Notifies that this bot for admins only and triggers email verification.

    :param state:
    :param message:
    :param sm:
    :return:
    """
    await message.answer(i18n.t('text.hello'))

    # checking if user already registered
    async with sm() as session:
        async with session.begin():
            # select users with sender id
            user = await session.execute((select(UserAdmin.tg_id).where(UserAdmin.tg_id == message.from_user.id)))
            user = user.one_or_none()
    if user is None:
        await request_email(message, state)
    else:
        await message.answer(i18n.t('text.correct_code'))


async def request_email(message: Message, state: FSMContext) -> None:
    """
    Requests email and updates state for unauthorised user.

    :param state:
    :param message:
    :return:
    """
    await message.answer(i18n.t('text.request_email'))
    await state.set_state(FSMRegistration.email_registration.state)


async def send_verification_code(message: Message, sm: sessionmaker, state: FSMContext) -> None:
    """
    Generates and sends verification code to provided email.

    :param state:
    :param message:
    :param sm:
    :return:
    """
    # checking email
    async with sm() as session:
        async with session.begin():
            # select users with email from message
            user = await session.execute((select(UserAdmin).where(UserAdmin.email == message.text)))
            user = user.one_or_none()
    if user is None:
        await message.answer(i18n.t('text.wrong_email'))
        return
    if user.UserAdmin.tg_id is not None and user.UserAdmin.tg_id != message.from_user.id:
        # TODO: decide: is it correct to rewrite user data?
        await message.answer(i18n.t('text.replacing_tg_account'))

    await message.answer(i18n.t('text.request_code'))
    code, creation_time, expiration_time = await send_code(message.text)
    await state.update_data(email=message.text,
                            verification_code=code,
                            created=creation_time,
                            expires=expiration_time)
    await state.set_state(FSMRegistration.code_confirmation.state)


async def check_code(message: Message, sm: sessionmaker, state: FSMContext):
    """
    Verifies code to grant user permission

    :param message:
    :param sm:
    :param state:
    :return:
    """
    user_data = await state.get_data()
    if datetime.now() > datetime.strptime(user_data['expires'], TIME_FORMAT):
        await message.answer(i18n.t('text.code_expired'), reply_markup=k.resend_code_keyboard)
    elif message.text != user_data.get('verification_code'):
        await message.answer(i18n.t('text.wrong_code'), reply_markup=k.resend_code_keyboard)
    else:
        # everything is fine, user authorised
        async with sm() as session:
            async with session.begin():
                # saving user information
                user_info = {
                    "tg_id": message.from_user.id,
                    "name": message.from_user.first_name,
                    "surname": message.from_user.last_name,
                    "email": user_data['email'],
                    "created_datetime": datetime.now()
                }
                user_update = update(UserAdmin).where(UserAdmin.email == user_data['email']).values(user_info)
                await session.execute(user_update)
        await message.reply(i18n.t('text.correct_code'))
        await state.finish()  # to remove unnecessary data
        await state.set_state(FSMAdminMenu.main_menu.state)


async def resend_code(call: CallbackQuery, state: FSMContext):
    """
    Handler for inline button. Resends code

    :param call:
    :param state:
    :return:
    """
    user_data = await state.get_data()
    if (datetime.now() - datetime.strptime(user_data['created'], TIME_FORMAT)).total_seconds() < 180:
        # code sent recently
        await call.answer(i18n.t('text.resend_code_timeout'), show_alert=True)
    else:
        code, creation_time, expiration_time = await send_code(user_data['email'])
        await call.answer("код отправлен")
        await state.update_data(verification_code=code,
                                created=creation_time,
                                expires=expiration_time)


async def change_email(call: CallbackQuery, state: FSMContext):
    await call.answer(i18n.t('text.request_email'))  # to avoid loading symbol on button
    await call.message.answer(i18n.t('text.request_email'))
    await state.set_state(FSMRegistration.email_registration.state)


def reg_admin_menu_handlers(dp: Dispatcher) -> None:
    """
    Register admin menu handlers in the dispatcher of the bot

    :param dp: Dispatcher of the bot
    :return:
    """
    dp.register_message_handler(greet, commands=["start"], state="*")
    dp.register_message_handler(send_verification_code, state=FSMRegistration.email_registration)
    dp.register_message_handler(check_code, state=FSMRegistration.code_confirmation)
    dp.register_callback_query_handler(resend_code, text="new_code_request", state=FSMRegistration.code_confirmation)
    dp.register_callback_query_handler(change_email, text="change_email", state=FSMRegistration.code_confirmation)
