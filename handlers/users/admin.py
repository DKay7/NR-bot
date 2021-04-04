import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.types import ReplyKeyboardRemove

from data.config import ADMIN_CHAT
from keyboards.default.reply_keyboards import get_not_master_kb, get_master_kb
from keyboards.inline.inline_keyboards import get_solution_kb
from loader import dp
from states.states import Master, Admin
from utils.db_api.db_commands import is_register, current_status, add_master






