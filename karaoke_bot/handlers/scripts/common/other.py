from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.keyboards import other_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.config import HELLO_TEXT, START_TEXT
# from karaoke_bot.models.sqlalchemy_models_without_polymorph import TelegramProfile, Account, Session
from karaoke_bot.models.sqlalchemy_data_utils import create_or_update_telegram_profile
from karaoke_bot.handlers.scripts.visitor.search_karaoke import search_karaoke
from karaoke_bot.handlers.scripts.common.register_telegram_user import register_telegram_user


async def start_command(message: types.Message, state: FSMContext):

    await register_telegram_user(message.from_user)

    args = message.get_args()
    if args is not None or args != '':  # если команда /start получена по внешней ссылке через QR code

        args = args.split('-')  # смотри delimeter внутри owner.generate_qr_code

        parameters = {}
        for arg in args:
            key, value = arg.split('=')
            parameters[key] = value

        match parameters.get('func'):
            case 'search_karaoke':
                karaoke_name = parameters.get('karaoke_name')
                if karaoke_name is not None:
                    message.text = karaoke_name
                    await message.answer(HELLO_TEXT, reply_markup=other_keyboard, parse_mode='HTML')
                    await search_karaoke(message=message, state=state)
    else:
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


def register_handlers(dispatcher: Dispatcher):

    dispatcher.register_callback_query_handler(callback_cancel_command, Text(equals='cancel'))
    dispatcher.register_message_handler(cancel_command, Text(equals='cancel', ignore_case=True), state='*')
    dispatcher.register_message_handler(cancel_command, commands=['cancel'], state='*')

    dispatcher.register_message_handler(start_command, commands=['start', 'help'], state='*')
