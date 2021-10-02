import asyncio
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from handlers.users.master import mailing
from keyboards.default.reply_keyboards import get_cancel_kb, get_admin_kb
from loader import dp
from sheets.connect import sp
from states.states import Admin
from utils.db_api.db_commands import get_ticket_by_id, add_ticket, archive


@dp.message_handler(Text(equals='Внести заявку'), chat_type=types.ChatType.PRIVATE, state=Admin.default)
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer('Введите срочность заявки. 1 -- срочная, 2 -- не срочная', reply_markup=get_cancel_kb())
    await Admin.get_priority.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Admin.get_category)
async def bot_start(message: types.Message, state: FSMContext):
    await state.update_data(ticket_priority=message.text)
    await message.answer('Введите категорию услуг')
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
                            confirm_date='-', accept_date='-', master='-',
                            final_work='-', is_client_happy='-', final_price='-',
                            denied_0='-', denied_1='-', denied_2='-', den_index=0)

    data = await state.get_data()
    id = add_ticket(data)

    text = f"Заявка {id}\n"\
           f"Приоритет: {data['ticket_priority']}"\
           f"Адрес: {data['address']}\n"\
           f"Категория: {data['category']}\n"\
           f"Дата выполнения: {data['date']}\n"\
           f"Стоимость: {data['price']}\n"\
           f"Описание:\n"\
           f"{data['desc']}"

    await message.answer('Заявка успешно создана',
                         reply_markup=get_admin_kb())
    await Admin.default.set()

    sp.update_table(ticket=get_ticket_by_id(id), table='tickets')
    await mailing(text, message.bot, id)

    await asyncio.sleep(2 * 24 * 60 * 60)
    archive(id)



