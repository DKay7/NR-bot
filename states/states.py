from aiogram.dispatcher.filters.state import StatesGroup, State


class Master(StatesGroup):
    not_master = State()
    master = State()
    get_name = State()
    get_reason = State()
    get_reason2 = State()
    get_dogov = State()


class Admin(StatesGroup):
    default = State()
    get_category = State()
    get_address = State()
    get_number = State()
    get_name = State()
    get_date = State()
    get_price = State()
    get_description = State()
