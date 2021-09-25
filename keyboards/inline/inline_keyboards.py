from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_solution_kb(uid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton('Принять', callback_data=f'accept_{uid}'))
    markup.insert(InlineKeyboardButton('Отклонить', callback_data=f'decline_{uid}'))
    return markup


def get_ticket_kb(uid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton('Принять', callback_data=f'ticket_ac_{uid}'))
    markup.insert(InlineKeyboardButton('Отклонить', callback_data=f'ticket_dc_{uid}'))
    return markup


def get_ticket_master_kb(uid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton('Принять', callback_data=f'ticket_ac_{uid}'))
    return markup


def get_client_kb(ticket_id):
    markup = InlineKeyboardMarkup(resize_keyboard=True)
    markup.insert(InlineKeyboardButton('Договорились', callback_data=f'good_{ticket_id}'))
    markup.insert(InlineKeyboardButton('Не договорились', callback_data=f'bad_{ticket_id}'))
    return markup


def get_master_ticket_kb(ticket_id):
    markup=InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton('Отменить', callback_data=f'cancel_{ticket_id}'))
    markup.insert(InlineKeyboardButton('Выполнен', callback_data=f'confirm_{ticket_id}'))
    return markup


def get_ticket_admin_cancel(tic_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton('Архивировать заявку', callback_data=f'ticket_archive_{tic_id}'))
    return markup

def get_master_admin_cancel(uid):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton('Удалить мастера', callback_data=f'master_delete_{uid}'))
    return markup