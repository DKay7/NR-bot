from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.types import ReplyKeyboardRemove

from sheets.connect import sp
from data.config import ADMIN_CHAT
from keyboards.default.reply_keyboards import get_not_master_kb, get_master_kb, get_admin_kb, get_cancel_kb
from keyboards.inline.inline_keyboards import get_solution_kb, get_ticket_kb, get_client_kb, get_master_ticket_kb, \
    get_ticket_master_kb
from loader import dp
from states.states import Master, Admin
from utils.db_api.db_commands import is_register, current_status, add_master, add_ticket, get_masters, is_aviable, \
    get_master_by_id, decline, get_tickets, confirm, get_actual_tickets


async def is_admin(uid, bot):
    a = await bot.get_chat_member(ADMIN_CHAT, uid)
    if a.status == 'creator' or a.status == 'administrator' or a.status == 'member':
        return True
    return False


async def mailing(text, bot, id):
    list = get_masters()

    markup = get_ticket_kb(id)
    for i in list:
        await bot.send_message(i['uid'], text, reply_markup=markup)


@dp.message_handler(CommandStart(), chat_type=types.ChatType.PRIVATE, state='*')
async def bot_start(message: types.Message, state: FSMContext):
    if not await is_admin(message.chat.id, message.bot):
        if not is_register(message.chat.id):
            await message.answer(f"Вы не являетесь мастером, но вы можете подать заявку",
                                 reply_markup=get_not_master_kb())
            await Master.not_master.set()
        else:
            await message.answer(f'Вы в главном меню, выберите что вас интересует', reply_markup=get_master_kb())
            await Master.master.set()
    else:
        await message.answer('Здравствуйте, вы в главном меню\nЗдесь вы можете создать новую заявку для мастеров',
                             reply_markup=get_admin_kb())
        await Admin.default.set()


@dp.message_handler(Text(equals='Стать мастером'), chat_type=types.ChatType.PRIVATE, state=Master.not_master)
async def bot_start(message: types.Message, state: FSMContext):
    if current_status():
        await message.answer('Введите своё Имя и Фамилию', reply_markup=ReplyKeyboardRemove())
        await Master.get_name.set()
    else:
        await message.answer('Извините, на данный момент приём новых мастеров закрыт. Попробуйте позже')


@dp.message_handler(Text(equals='Мои заявки'), chat_type=types.ChatType.PRIVATE, state=Master.master)
async def bot_start(message: types.Message, state: FSMContext):
    tickets = get_tickets(message.chat.id)
    for data in tickets:
        text = f"""Заявка {data['id']}
Адрес: {data['address']}
Категория: {data['category']}
Дата выполнения: {data['date']}
Стоимость: {data['price']}
Номер клиента: {data["number"]}
Имя: {data["name"]}
Описание:
{data['desc']}"""
        await state.update_data(price=data['price'])
        await message.answer(text, reply_markup=get_master_ticket_kb(data['id']))


@dp.message_handler(Text(equals='Актуальные заявки'), chat_type=types.ChatType.PRIVATE, state=Master.master)
async def bot_start(message: types.Message, state: FSMContext):
    tickets = get_actual_tickets()
    for data in tickets:
        text = f"""Заявка {data['id']}
Адрес: {data['address']}
Категория: {data['category']}
Дата выполнения: {data['date']}
Стоимость: {data['price']}
Номер клиента: {data["number"]}
Имя: {data["name"]}
Описание:
{data['desc']}"""
        await message.answer(text, reply_markup=get_ticket_master_kb(data['id']))


@dp.callback_query_handler(Text(startswith='confirm_'), chat_type=types.ChatType.PRIVATE,
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup('')
    data = await state.get_data()
    id = int(call.data.split('_')[1])

    confirm(id)
    sp.update_table()

    await call.message.answer(f'Заявка {id} закрыта! Спасибо за сотрудничество!!!')
    await call.message.bot.send_message(ADMIN_CHAT, f"Заявка {id} закрыта мастером <a href='tg://user?id={call.message.chat.id}'>{get_master_by_id(call.message.chat.id)}</a>\n"
                                                    f'Сумма: {data["price"]}')
    await call.message.delete()


@dp.callback_query_handler(Text(startswith='cancel_'), chat_type=types.ChatType.PRIVATE,
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup('')
    data=await state.get_data()
    id = int(call.data.split('_')[1])
    await call.message.answer(f'Укажите причину отмены заявки')
    await Master.get_reason2.set()

    decline(id)
    sp.update_table()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Master.get_reason2)
async def bot_start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = f'''Заявка {data['id']}
<a href='tg://user?id={message.chat.id}'>{get_master_by_id(message.chat.id)}</a> отменил заявку по причине:
{message.text}'''
    await message.bot.send_message(ADMIN_CHAT, text)
    await message.answer('Ваш ответ передан администрации', reply_markup=get_master_kb())
    await Master.master.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Master.get_name)
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer(f'Ваша заявка отправлена, ожидайте решения администрации')
    text = f"Новая заявка в мастера\n" \
           f"<a href='tg://user?id={message.chat.id}'>{message.text}</a>"
    await message.bot.send_message(ADMIN_CHAT, text, reply_markup=get_solution_kb(message.chat.id))
    add_master(message.chat.id, message.text)
    await Master.master.set()


@dp.message_handler(Text(equals='Отменить', ignore_case=True), chat_type=types.ChatType.PRIVATE, state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer('Вы вернулись в главное меню', reply_markup=get_admin_kb())
    await Admin.default.set()


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

    sp.update_table()

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


@dp.callback_query_handler(Text(startswith='ticket_ac_'), chat_type=types.ChatType.PRIVATE,
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    id = int(call.data.split('_')[2])
    r = is_aviable(id, call.message.chat.id)
    if r:
        await call.message.bot.send_message(ADMIN_CHAT,
                                            f"<a href='tg://user?id={call.message.chat.id}'>{get_master_by_id(call.message.chat.id)}</a> принял заявку {id}")
        await call.message.edit_reply_markup('')
        await call.message.answer(
            f'Вам необходимо связаться с клиентом и договориться обо всём\n\nНомер клиента: {r["number"]}\nИмя: {r["name"]}',
            reply_markup=get_client_kb(id))
    else:
        await call.answer('Данную заявку уже взял другой мастер', show_alert=True)
        await call.message.delete()


@dp.callback_query_handler(Text(startswith='ticket_dc_'), chat_type=types.ChatType.PRIVATE,
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()


@dp.callback_query_handler(Text(startswith='bad_'), chat_type=types.ChatType.PRIVATE,
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup('')
    id = int(call.data.split('_')[1])
    await state.update_data(id=id)
    decline(id)
    sp.update_table()
    await call.message.answer('Укажите причину по которой не получилось договориться')
    await Master.get_reason.set()


@dp.callback_query_handler(Text(startswith='good_'), chat_type=types.ChatType.PRIVATE,
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup('')
    id = int(call.data.split('_')[1])
    await state.update_data(id=id)
    await call.message.answer('Укажите о чём вы договорились')
    await Master.get_dogov.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Master.get_reason)
async def bot_start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = f'''Заявка {data['id']}
<a href='tg://user?id={message.chat.id}'>{get_master_by_id(message.chat.id)}</a> не договорился с клиентом по причине:
{message.text}'''
    await message.bot.send_message(ADMIN_CHAT, text)
    await message.answer('Ваш ответ передан администрации', reply_markup=get_master_kb())
    await Master.master.set()


@dp.message_handler(chat_type=types.ChatType.PRIVATE, state=Master.get_dogov)
async def bot_start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = f'''Заявка {data['id']}
<a href='tg://user?id={message.chat.id}'>{get_master_by_id(message.chat.id)}</a> договорился с клиентом и указал:
{message.text}'''
    await message.bot.send_message(ADMIN_CHAT, text)
    await message.answer('Ваше сообщение передано администрации\n\nПосле выполнения работы не забудьте отметить заказ '
                         'выполненным', reply_markup=get_master_kb())
    await Master.master.set()


