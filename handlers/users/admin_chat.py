from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.types import ReplyKeyboardRemove

from sheets.connect import sp
from handlers.users.master import mailing
from keyboards.default.reply_keyboards import get_not_master_kb, get_master_kb
from loader import dp
from states.states import Master
from utils.db_api.db_commands import is_registered_master, approve_master, current_status, set_status, delete_master, archive, \
    get_masters, get_ticket_by_id, update_ticket, get_master_by_uid


@dp.callback_query_handler(Text(startswith='accept'), chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    uid = int(call.data.split('_')[1])
    approve_master(uid)

    await call.message.edit_text(call.message.text + '\n\nПРИНЯТ', reply_markup=None)
    await call.message.bot.send_message(uid,
                                        'Вы приняты, в данном чате вы будете получать уведомления о новых заявках и '
                                        'управлять ими',
                                        reply_markup=get_master_kb())

    sp.update_table(table='masters', master=get_master_by_uid(uid))


@dp.callback_query_handler(Text(startswith='decline'), chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                           state='*')
async def bot_start(call: types.CallbackQuery, state: FSMContext):
    uid = int(call.data.split('_')[1])
    await call.message.bot.send_message(uid, 'Вам было отказано', reply_markup=ReplyKeyboardRemove())
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


@dp.message_handler(Text(startswith='УДАЛИТЬ МАСТЕРА'),
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state='*')
async def asd(message: types.Message):
    master_uid = int(message.text.split(' ')[2])
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

    sp.delete_master(master)


@dp.message_handler(Text(startswith='АРХИВ'),
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state='*')
async def asd(message: types.Message):
    uid = int(message.text.split(' ')[2])

    if archive(uid):
        await message.answer(f'Заявка {uid} помещена в архив')

    sp.update_table(ticket=get_ticket_by_id(uid), table='tickets')


@dp.message_handler(Text(startswith='МАСТЕРАМ'),
                    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], state='*')
async def asd(message: types.Message):
    text = message.text.replace('МАСТЕРАМ', '')
    await mailing_text(text, message.bot)
    await message.answer('Рассылка успешно выполнена')


@dp.message_handler(Text(startswith='РАССЫЛКА'),
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