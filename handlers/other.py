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


async def menu_command(message: types.Message, state: FSMContext):
    await state.finish()

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="My karaoke", callback_data='my_karaoke'))
    keyboard.insert(InlineKeyboardButton(text="My orders", callback_data='my_orders'))
    await message.answer('Это ваш кабинет пользователя, что вы хотите сделать?', reply_markup=keyboard)


async def callback_my_karaoke(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Managed", callback_data='managed_karaoke'))
    keyboard.insert(InlineKeyboardButton(text="Membering", callback_data='membering_karaoke'))
    keyboard.add(InlineKeyboardButton(text='<< Back to main menu', callback_data='back_to_main_menu'))
    await callback.message.edit_text('Информация о ваших караоке', reply_markup=keyboard)


async def callback_managed_karaoke(callback: types.CallbackQuery):
    user_info, owner_info = sqlite_db.sql_get_user_status(callback.from_user.id)

    owner_info = [karaoke_name[0] for karaoke_name in owner_info]
    owner_text = "<b>At the moment you own these karaoke:</b>\n- " + '\n- '.join(owner_info) + '\n\n'
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='<< Back to karaoke info', callback_data='my_karaoke'))
    await callback.message.edit_text(owner_text, reply_markup=keyboard)


async def callback_back_to_main_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="My karaoke", callback_data='my_karaoke'))
    keyboard.insert(InlineKeyboardButton(text="My orders", callback_data='my_orders'))
    await callback.message.edit_text('Это ваш кабинет пользователя, что вы хотите сделать?', reply_markup=keyboard)


async def status_command(message: types.Message, state: FSMContext):
    await state.finish()

    user_info, owner_info = sqlite_db.sql_get_user_status(message.from_user.id)
    if owner_info:  # если список караоке не пустой
        owner_info = [karaoke_name[0] for karaoke_name in owner_info]
        owner_text = "<b>At the moment you own these karaoke:</b>\n- " + '\n- '.join(owner_info) + '\n\n'
    else:
        owner_text = ''

    has_karaoke = False
    if user_info is not None:  # если пользователь такой есть
        active_karaoke, karaoke_list = user_info
        karaoke_list = karaoke_list.split('; ')
        if karaoke_list:
            has_karaoke = True
        user_text = "<b>At the moment you are a member of these karaoke:</b>\n- " + '\n- '.join(karaoke_list) + '\n\n'
        user_text += f"<b>Active karaoke:</b>\n🎤 {active_karaoke}"
    else:
        user_text = ''

    keyboard = InlineKeyboardMarkup()
    text = owner_text + user_text

    if text:
        keyboard.add(InlineKeyboardButton(text='Change active karaoke', callback_data='change_active_karaoke'))
        if not has_karaoke:
            keyboard = None
        await message.answer(text, parse_mode='HTML', reply_markup=keyboard)
    else:
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
            button = InlineKeyboardButton(text=karaoke_name, callback_data=f'change_to {karaoke_name}')

            if i % 2 == 0:
                keyboard.add(button)
            else:
                keyboard.insert(button)
        await callback.message.edit_reply_markup(keyboard)


async def callback_change_to(callback: types.CallbackQuery):
    karaoke_name = callback.data.split(' ')[-1]
    user_id = callback.from_user.id
    await sqlite_db.sql_update_user_active_karaoke(active_karaoke=karaoke_name, user_id=user_id)

    rows = callback.message.html_text.split('\n')
    rows[-1] = f"🎤 {karaoke_name}"

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Change active karaoke', callback_data='change_active_karaoke'))
    await callback.message.edit_text('\n'.join(rows), reply_markup=keyboard, parse_mode='HTML')


def register_handlers_other(dispatcher: Dispatcher):

    dispatcher.register_callback_query_handler(callback_cancel_command, Text(equals='cancel'))
    dispatcher.register_message_handler(cancel_command, Text(equals='cancel', ignore_case=True), state='*')
    dispatcher.register_message_handler(cancel_command, commands=['cancel'], state='*')

    dispatcher.register_message_handler(status_command, Text(equals="Status", ignore_case=True), state='*')
    dispatcher.register_message_handler(status_command, commands=['status'], state='*')

    dispatcher.register_message_handler(menu_command, Text(equals="menu", ignore_case=True), state='*')
    dispatcher.register_message_handler(menu_command, commands=['menu'], state='*')

    dispatcher.register_message_handler(start_command, commands=['start', 'help'], state='*')

    dispatcher.register_callback_query_handler(callback_change_active_karaoke, Text(equals='change_active_karaoke'))
    dispatcher.register_callback_query_handler(callback_change_to, Text(startswith='change_to'))

    dispatcher.register_callback_query_handler(callback_my_karaoke, Text(equals='my_karaoke'))
    dispatcher.register_callback_query_handler(callback_back_to_main_menu, Text(equals='back_to_main_menu'))
    dispatcher.register_callback_query_handler(callback_managed_karaoke, Text(equals='managed_karaoke'))



