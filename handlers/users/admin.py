from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Text

from handlers.users.master import mailing
from keyboards.default.reply_keyboards import get_cancel_kb, get_admin_kb
from loader import dp
from sheets.connect import sp
from states.states import Admin
from utils.db_api.db_commands import get_ticket_by_id, add_ticket, get_actual_tickets, archive, get_all_masters
from utils.db_api.db_commands import set_master_status_deleted, get_master_by_uid
from keyboards.inline.inline_keyboards import get_ticket_admin_cancel, get_master_admin_cancel


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
                            confirm_date='-', accept_date='-', master='-',
                            final_work='-', is_client_happy='-', final_price='-',
                            denied_0='-', denied_1='-', denied_2='-', den_index=0)

    data = await state.get_data()
    id = add_ticket(data)

    text = f"Заявка {id}\n"\
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

@dp.message_handler(Text(equals='АРХИВ'), chat_type=types.ChatType.PRIVATE, state=Admin.default)
async def bot_start(message: types.Message, state: FSMContext):
    tickets = get_actual_tickets()


    if not tickets:
        await message.answer("На данный момент нет открытых заявок с неназначенным мастером.")

    else:
        for data in tickets:
            text = f"Заявка {data['id']}\n\n" \
                   f"Адрес: {data['address']}\n" \
                   f"Категория: {data['category']}\n" \
                   f"Дата выполнения: {data['date']}\n" \
                   f"Стоимость: {data['price']}\n" \
                   f"Имя: {data['name']}\n" \
                   f"Описание:\n" \
                   f"{data['desc']}"

            await message.answer(text, reply_markup=get_ticket_admin_cancel(data['id']))


@dp.callback_query_handler(Text(startswith=f'ticket_archive_'), chat_type=types.ChatType.PRIVATE, state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup('')
    id_ = int(call.data.split('_')[2])
    archive(id_)
    sp.update_table(ticket=get_ticket_by_id(id_), table='tickets')
    await call.message.answer(f'Заявка отправлена в архив')

@dp.message_handler(Text(equals='Мастера на удаление'), chat_type=types.ChatType.PRIVATE, state=Admin.default)
async def get_masters_list_to_delete(message: types.Message, state: FSMContext):
    masters = get_all_masters()

    if not masters:
        await message.answer("На данный момент нет мастеров")

    else:
        for data in masters:
            text = f"<a href='tg://user?id={message.chat.id}'>" \
                   f"{data['name']}</a>\n" \
                   f"Контактный телефон: {data['phone']}" 

            await message.answer(text, reply_markup=get_master_admin_cancel(data['uid'])) 

@dp.callback_query_handler(Text(startswith=f'master_delete_'), chat_type=types.ChatType.PRIVATE, state='*')
async def delete_chosen_master(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup('')
    id_ = int(call.data.split('_')[2])
    set_master_status_deleted(id_)
    sp.update_table(master=get_master_by_uid(id_), table='masters')
    await call.message.answer(f'Мастеру присвоена категория на удаление')
