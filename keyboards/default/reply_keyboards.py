from aiogram.types import ReplyKeyboardMarkup


def get_not_master_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.insert('Стать мастером')
    return markup


def get_master_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.insert('Мои заявки')
    markup.insert('Актуальные заявки')
    return markup

def to_main_menu_master_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.insert('Перейти в главное меню')
    return markup

def get_admin_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.insert('Внести заявку')
    return markup


def get_cancel_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.insert('Отменить')
    return markup
