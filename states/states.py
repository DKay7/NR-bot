from aiogram.dispatcher.filters.state import StatesGroup, State


class Master(StatesGroup):
    not_master = State()
    master = State()
    get_name = State()
    get_speciality = State()
    get_phone = State()
    get_address = State()

    get_reason = State()
    get_reason2 = State()
    get_dogov = State()
    get_final_price = State()


class Admin(StatesGroup):
    default = State()
    get_category = State()
    get_address = State()
    get_number = State()
    get_name = State()
    get_date = State()
    get_price = State()
    get_description = State()
    get_final_price = State()
