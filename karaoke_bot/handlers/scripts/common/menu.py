from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.keyboards import other_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.models.sqlalchemy_models_without_polymorph import TelegramProfile, Account, Session
from karaoke_bot.models.sqlalchemy_data_utils import create_or_update_telegram_profile
from karaoke_bot.models.sqlalchemy_data_utils import get_account_roles, get_visitor_karaoke_names, \
    get_visitor_karaokes_data
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, EmptyFieldError
from karaoke_bot.handlers.scripts.common.other import register_telegram_user
from karaoke_bot.repository.sqlalchemy_repository import Repository
import json


async def menu_command(message: types.Message, state: FSMContext):
    await state.finish()

    # data = Repository.get(
    #     lookup_table_name='telegram_profiles',
    #     filter_by={'id': message.from_user.id},
    #     model_attr=[
    #         'account',
    #         'visitor'
    #     ],
    #     search_attr={
    #         'karaokes': {
    #             'name': {},
    #             'owner': {
    #                 'account': {
    #                     'telegram_profile': {
    #                         'id': {},
    #                         'username': {}
    #                     }
    #                 }
    #             },
    #             'is_active': {},
    #             'avatar_id': {},
    #             'description': {}
    #
    #         }
    #     }
    # )
    # print(json.dumps(data, indent=4, ensure_ascii=False))

    try:
        is_visitor, is_owner, is_moderator, is_administrator = get_account_roles(message.from_user.id)
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
        await register_telegram_user(message.from_user)
        await menu_command(message=message, state=state)
    else:
        keyboard = InlineKeyboardMarkup()
        if is_visitor:
            keyboard.add(InlineKeyboardButton(text="My orders", callback_data='menu my_orders'))
        if is_owner:
            keyboard.insert(InlineKeyboardButton(text="My karaoke", callback_data='menu my_karaoke'))

        await message.answer('MENU', reply_markup=keyboard)


async def callback_menu_command(callback: types.CallbackQuery):
    await callback.answer()

    keyboard = InlineKeyboardMarkup()
    callback_data = callback.data.split(' ')[1:]
    match callback_data:
        case ('my_orders',):
            pass
        case ('my_karaoke',):
            keyboard.add(InlineKeyboardButton(text="Managed", callback_data='menu managed_karaoke'))
            keyboard.insert(InlineKeyboardButton(text="Membering", callback_data='menu membering_karaoke'))
            keyboard.add(InlineKeyboardButton(text='<< Back', callback_data='menu back'))
            await callback.message.edit_text('Information about your karaoke', reply_markup=keyboard)
        case ('managed_karaoke'):
            try:
                pass
            except:
                pass
        case ('membering_karaoke',):
            try:
                karaokes_data = get_visitor_karaokes_data(telegram_id=callback.from_user.id)
            except EmptyFieldError as e:
                print(f"ERROR OCCURRED: {e}")
            else:
                text = 'KARAOKE  |  OWNER  |  SUBSCRIBERS  |  IS_ACTIVE\n\n'
                for karaoke_name, karaoke_data in karaokes_data.items():
                    username = karaoke_data['owner']['username']
                    is_active = '✅ ACTIVE' if karaoke_data['is_active'] else '❌ INACTIVE'
                    subscribers_amount = karaoke_data['subscribers_amount']
                    text += f"{karaoke_name}  |  @{username}  |  {subscribers_amount}  |  {is_active}\n"
                keyboard.add(InlineKeyboardButton(text='<< Back to karaoke info', callback_data='menu my_karaoke'))
                await callback.message.edit_text(text, reply_markup=keyboard)
        case ('back',):
            keyboard.add(InlineKeyboardButton(text="My karaoke", callback_data='menu my_karaoke'))
            keyboard.insert(InlineKeyboardButton(text="My orders", callback_data='menu my_orders'))
            await callback.message.edit_text('MENU', reply_markup=keyboard)


def register_handlers(dispatcher: Dispatcher):

    dispatcher.register_message_handler(menu_command, Text(equals="menu", ignore_case=True), state='*')
    dispatcher.register_message_handler(menu_command, commands=['menu'], state='*')

    dispatcher.register_callback_query_handler(callback_menu_command, Text(startswith='menu'))
