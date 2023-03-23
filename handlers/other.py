from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from keyboards import other_keyboard
from data_base import sqlite_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import START_TEXT


async def start_command(message: types.Message):
    await message.answer(START_TEXT, reply_markup=other_keyboard, parse_mode='HTML')


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

    len_flag = False
    if user_info is not None:  # если пользователь такой есть
        active_karaoke, karaoke_list = user_info
        karaoke_list = karaoke_list.split('; ')
        if karaoke_list:
            len_flag = True
        user_text = "<b>At the moment you are a member of these karaoke:</b>\n- " + '\n- '.join(karaoke_list) + '\n\n'
        user_text += f"<b>Active karaoke:</b>\n🎤 {active_karaoke}"
    else:
        user_text = ''

    text = owner_text + user_text

    if text:
        keyboard = None
        if len_flag:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text='Change active karaoke', callback_data='change_active_karaoke'))
        await message.answer(text, parse_mode='HTML', reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="✅ Yes", callback_data='search_karaoke'))
        keyboard.insert(InlineKeyboardButton(text="❌ No", callback_data='cancel'))
        await message.answer("Sorry, it seems you are a new user and there is no information about you yet.\n\n"
                             "🖊 Do you want to <b>subscribe</b> to karaoke and order music?",
                             reply_markup=keyboard,
                             parse_mode='HTML')


async def callback_change_active_karaoke(callback: types.CallbackQuery):
    user_info, _ = sqlite_db.sql_get_user_status(callback.from_user.id)
    if user_info is not None:  # если пользователь такой есть
        active_karaoke, karaoke_list = user_info
        karaoke_list = karaoke_list.split('; ')

        keyboard = InlineKeyboardMarkup()
        for i in range(len(karaoke_list)):
            karaoke_name = karaoke_list[i]
            if i % 2 == 0:
                keyboard.add(InlineKeyboardButton(text=karaoke_name, callback_data='search_karaoke'))
            else:
                keyboard.insert(InlineKeyboardButton(text=karaoke_name, callback_data='cancel'))
            await callback.message.edit_reply_markup(keyboard)



def register_handlers_other(dispatcher: Dispatcher):

    dispatcher.register_callback_query_handler(callback_cancel_command, Text(equals='cancel'))
    dispatcher.register_message_handler(cancel_command, Text(equals='cancel', ignore_case=True), state='*')
    dispatcher.register_message_handler(cancel_command, commands=['cancel'], state='*')

    dispatcher.register_message_handler(status_command, Text(equals="Status", ignore_case=True), state='*')
    dispatcher.register_message_handler(status_command, commands=['status'], state='*')

    dispatcher.register_message_handler(start_command, commands=['start', 'help'], state='*')
    dispatcher.register_callback_query_handler(callback_change_active_karaoke, Text(equals='change_active_karaoke'))
