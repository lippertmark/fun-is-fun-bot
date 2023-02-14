from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMRegistration(StatesGroup):
    email_registration = State()
    code_confirmation = State()


class FSMAdminMenu(StatesGroup):
    main_menu = State()
    delete_event_reason = State()
