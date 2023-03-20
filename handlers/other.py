from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from keyboards import client_keyboard
from data_base import sqlite_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import START_TEXT


async def start_command(message: types.Message):
    await message.answer(START_TEXT, reply_markup=client_keyboard, parse_mode='HTML')


async def cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Ok")
        return None
    await state.finish()
    await message.reply("Ok")


async def callback_cancel_command(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await cancel_command(callback.message, state)


async def status_command(message: types.Message, state: FSMContext):
    await state.finish()

    user_info, owner_info = sqlite_db.sql_get_user_status(message.from_user.id)

    if owner_info:  # если список караоке не пустой
        owner_info = [karaoke_name[0] for karaoke_name in owner_info]
        owner_text = "<b>At the moment you own these karaoke:</b>\n- " + '\n- '.join(owner_info) + '\n\n'
    else:
        owner_text = ''

    if user_info is not None:  # если пользователь такой есть
        active_karaoke, karaoke_list = user_info
        karaoke_list = karaoke_list.split('; ')
        user_text = "<b>At the moment you are a member of these karaoke:</b>\n- " + '\n- '.join(karaoke_list) + '\n\n'
        user_text += f"<b>Active karaoke:</b>\n🎤 {active_karaoke}"
    else:
        user_text = ''

    text = owner_text + user_text

    if text:
        await message.answer(text, parse_mode='HTML')
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="✅ Yes", callback_data='search_karaoke'))
        keyboard.insert(InlineKeyboardButton(text="❌ No", callback_data='cancel'))
        await message.answer("Sorry, it seems you are a new user and there is no information about you yet.\n\n"
                             "🖊 Do you want to <b>subscribe</b> to karaoke and order music?",
                             reply_markup=keyboard,
                             parse_mode='HTML')


def register_handlers_other(dispatcher: Dispatcher):

    dispatcher.register_callback_query_handler(callback_cancel_command, Text(equals='cancel'))
    dispatcher.register_message_handler(cancel_command, Text(equals='cancel', ignore_case=True), state='*')
    dispatcher.register_message_handler(cancel_command, commands=['cancel'], state='*')

    dispatcher.register_message_handler(status_command, Text(equals="Status", ignore_case=True), state='*')
    dispatcher.register_message_handler(status_command, commands=['status'], state='*')

    dispatcher.register_message_handler(start_command, commands=['start', 'help'], state='*')
