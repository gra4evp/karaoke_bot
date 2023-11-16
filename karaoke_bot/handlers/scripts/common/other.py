from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.keyboards import other_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.config import START_TEXT
# from karaoke_bot.models.sqlalchemy_models_without_polymorph import TelegramProfile, Account, Session
from karaoke_bot.models.sqlalchemy_data_utils import create_or_update_telegram_profile


async def register_telegram_user(user: types.User):
    try:
        create_or_update_telegram_profile(user)
    except Exception as e:
        print(f"Error occurred: {e}")


async def start_command(message: types.Message):
    args = message.get_args()
    if args is not None or args != '':

        args = args.split('-')

        parameters = {}
        for arg in args:
            key, value = arg.split('=')
            parameters[key] = value

        print(parameters)

    await message.answer(START_TEXT, reply_markup=other_keyboard, parse_mode='HTML')
    await register_telegram_user(message.from_user)


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


def register_handlers(dispatcher: Dispatcher):

    dispatcher.register_callback_query_handler(callback_cancel_command, Text(equals='cancel'))
    dispatcher.register_message_handler(cancel_command, Text(equals='cancel', ignore_case=True), state='*')
    dispatcher.register_message_handler(cancel_command, commands=['cancel'], state='*')

    dispatcher.register_message_handler(start_command, commands=['start', 'help'], state='*')
