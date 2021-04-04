from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from handlers.users.master import mailing
from keyboards.default.reply_keyboards import get_cancel_kb, get_admin_kb
from loader import dp
from sheets.connect import sp
from states.states import Admin
from utils.db_api.db_commands import get_ticket_by_id, add_ticket


@dp.message_handler(Text(equals='Внести заявку'), chat_type=types.ChatType.PRIVATE, state=Admin.default)
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer('Введите категорию услуг', reply_markup=get_cancel_kb())
    await Admin.get_category.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Admin.get_category)
async def bot_start(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer('Введите адрес (метро)')
    await Admin.get_address.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Admin.get_address)
async def bot_start(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer('Введите номер клиента')
    await Admin.get_number.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Admin.get_number)
async def bot_start(message: types.Message, state: FSMContext):
    await state.update_data(number=message.text)
    await message.answer('Введите имя клиента')
    await Admin.get_name.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Admin.get_name)
async def bot_start(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите дату выполнения работ')
    await Admin.get_date.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Admin.get_date)
async def bot_start(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer('Введите стоимость')
    await Admin.get_price.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Admin.get_price)
async def bot_start(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer('Введите описание или ссылку на telegra.ph статью')
    await Admin.get_description.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Admin.get_description)
async def bot_start(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text, status=0, create_date=datetime.now().strftime("%d.%m.%Y %X"),
                            confirm_date='-', accept_date='-', master='-')
    data = await state.get_data()
    id = add_ticket(data)

    text = f"""Заявка {id}
            Адрес: {data['address']}
            Категория: {data['category']}
            Дата выполнения: {data['date']}
            Стоимость: {data['price']}
            Описание:
            {data['desc']}"""

    await message.answer('Заявка успешно создана',
                         reply_markup=get_admin_kb())
    await Admin.default.set()
    await mailing(text, message.bot, id)

    sp.update_table(get_ticket_by_id(id))




