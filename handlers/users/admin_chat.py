from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.types import ReplyKeyboardRemove

from keyboards.inline.inline_keyboards import get_ticket_admin_cancel, get_master_admin_cancel
from sheets.connect import sp
from handlers.users.master import mailing
from keyboards.default.reply_keyboards import get_not_master_kb, get_master_kb, to_main_menu_master_kb
from loader import dp
from states.states import Master, Admin
from utils.db_api.db_commands import is_registered_master, approve_master, current_status, set_status, delete_master, \
    archive, \
    get_masters, get_ticket_by_id, update_ticket, get_master_by_uid, get_actual_tickets, get_all_masters, \
    set_master_status_deleted, confirm, decline


@dp.callback_query_handler(Text(startswith='accept'), chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    uid = int(call.data.split('_')[1])
    approve_master(uid)

    await call.message.edit_text(call.message.text + '\n\nПРИНЯТ', reply_markup=None)
    await call.message.bot.send_message(uid,
                                        'Вы приняты, в данном чате вы будете получать уведомления о новых заявках и '
                                        'управлять ими',
                                        reply_markup=to_main_menu_master_kb())

    sp.update_table(table='masters', master=get_master_by_uid(uid))


@dp.callback_query_handler(Text(startswith='decline'), chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    uid = int(call.data.split('_')[1])
    await call.message.bot.send_message(uid, 'Вам было отказано', reply_markup=to_main_menu_master_kb())
    await call.message.edit_text(call.message.text + '\n\nОТКАЗАНО', reply_markup=None)
    delete_master(uid)
    await Master.not_master.set()


@dp.message_handler(Text(equals='СТАТУС'), chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state='*')
async def bot_start(message: types.Message, state: FSMContext):
    if current_status():
        set_status(False)
        await message.answer('Прием мастеров закрыт')
    else:
        set_status(True)
        await message.answer('Прием мастеров открыт')


@dp.message_handler(Text(startswith='УДАЛИТЬ'),
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state='*')
async def asd(message: types.Message):
    master_uid = int(message.text.split(' ')[1])
    master = get_master_by_uid(master_uid)

    if master is None:
        await message.answer(f'Мастера с id {master_uid} не существует')
        return

    delete_master(master_uid)
    try:
        await message.bot.send_message(master_uid, 'Вы были удалены из списка мастеров', reply_markup=ReplyKeyboardRemove())
        await message.answer(f'Мастер {master_uid} успешно удалён')
    except:
        pass


@dp.message_handler(Text(startswith='РАССЫЛКА'),
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state='*')
async def asd(message: types.Message):
    text = message.text.replace('МАСТЕРАМ', '')
    await mailing_text(text, message.bot)
    await message.answer('Рассылка успешно выполнена')


@dp.message_handler(Text(startswith='РАССЫЛКА_ЗАЯВКИ'),
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state='*')
async def asd(message: types.Message):
    uid = int(message.text.split(' ')[1])
    data = get_ticket_by_id(uid)
    text = f"""Заявка {uid}
    Адрес: {data['address']}
    Категория: {data['category']}
    Дата выполнения: {data['date']}
    Стоимость: {data['price']}
    Описание:
    {data['desc']}"""
    await mailing(text, message.bot, uid)
    await message.answer('Рассылка успешно выполнена')


@dp.message_handler(Text(startswith='ВЕРНУТЬ И РАЗОСЛАТЬ'),
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state='*')
async def asd(message: types.Message):
    uid = int(message.text.split(' ')[3])
    update_ticket(uid, 0)

    sp.update_table(ticket=get_ticket_by_id(uid), table='tickets')
    data = get_ticket_by_id(uid)

    text = f"""Заявка {uid}
        Адрес: {data['address']}
        Категория: {data['category']}
        Дата выполнения: {data['date']}
        Стоимость: {data['price']}
        Описание:
        {data['desc']}"""
    await mailing(text, message.bot, uid)
    await message.answer('Рассылка успешно выполнена')


async def mailing_text(text, bot):
    list = get_masters()
    for i in list:
        await bot.send_message(i['uid'], text)


@dp.message_handler(Text(equals='АРХИВ'), chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state="*")
async def archive_ticket(message: types.Message, state: FSMContext):
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


@dp.message_handler(Text(equals='ЗАКРТЫТЬ'), chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state="*")
async def archive_ticket(message: types.Message, state: FSMContext):
    ticket_status = int(message.text.split(' ')[1])
    ticket_id = int(message.text.split(' ')[2])

    if ticket_status == 1:
        data = {
            'final_price': '-',
            'final_work': '-',
            'is_client_happy': '-'
        }
        confirm(ticket_id, data)
        await message.answer(f'Заявка завершена успешно')

    elif ticket_id == 2:
        decline(ticket_id, '-')
        await message.answer(f'Заявка отменена')

    elif ticket_id == 3:
        archive(ticket_id)
        await message.answer(f'Заявка отправлена в архив')

    sp.update_table(ticket=get_ticket_by_id(ticket_id), table='tickets')


@dp.callback_query_handler(Text(startswith=f'ticket_archive_'), chat_type=[types.ChatType.GROUP,
                                                                           types.ChatType.SUPERGROUP], state='*')
async def archive_ticket_button(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup('')
    id_ = int(call.data.split('_')[2])
    archive(id_)
    sp.update_table(ticket=get_ticket_by_id(id_), table='tickets')
    await call.message.answer(f'Заявка отправлена в архив')


@dp.message_handler(Text(equals='СПИСОК'), chat_type=[types.ChatType.GROUP,
                                                      types.ChatType.SUPERGROUP], state="*")
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


@dp.callback_query_handler(Text(startswith=f'master_delete_'), chat_type=[types.ChatType.GROUP,
                                                                          types.ChatType.SUPERGROUP], state='*')
async def delete_chosen_master(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup('')
    id_ = int(call.data.split('_')[2])
    set_master_status_deleted(id_)
    sp.update_table(master=get_master_by_uid(id_), table='masters')
    await call.message.answer(f'Мастеру присвоена категория на удаление')
