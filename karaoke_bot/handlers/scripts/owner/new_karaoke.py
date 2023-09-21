from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from string import ascii_letters, digits

from karaoke_bot.create_bot import bot
from karaoke_bot.states.owner_states import NewKaraoke
from karaoke_bot.handlers.scripts.common.other import register_telegram_user
from karaoke_bot.handlers.scripts.visitor.search_karaoke import search_karaoke
from karaoke_bot.models.sqlalchemy_data_utils import karaoke_not_exists, create_karaoke, create_karaoke_session
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError
from karaoke_bot.keyboards.owner.new_karaoke_keyboards import keyboards


async def new_karaoke_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['owner'] = message.from_user

    await message.answer(f"Come up with a <b>NAME</b> for your karaoke.\n\n"
                         f"To make it easier for users to find you, "
                         f"you can come up with a <b>NAME</b> similar to your establishment.", parse_mode='HTML')

    await NewKaraoke.name.set()


async def karaoke_name_registration(message: types.Message, state: FSMContext):
    karaoke_name = message.text
    if karaoke_not_exists(karaoke_name):
        async with state.proxy() as data:
            data['karaoke_name'] = karaoke_name
            data['message_karaoke_name'] = message

        current_state = await state.get_state()
        if current_state == 'NewKaraoke:name':
            await NewKaraoke.avatar.set()
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text='Skip', callback_data='new_karaoke skip avatar'))
            await message.answer(
                "Now send the 🖼 <b>PHOTO</b> you want to set as your karaoke avatar.",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await message.answer(
                '✅ Success! <b>NAME</b> updated.',
                reply_markup=keyboards['back_to'],
                parse_mode='HTML'
            )
    else:
        await message.reply("🔒 Sorry, this <b>NAME</b> is already taken.", parse_mode='HTML')


async def karaoke_name_is_invalid(message: types.Message):
    await message.reply(
        "The <b>NAME</b> must be presented in text and contain't any punctuation marks, "
        "except for: <b>\"$*&_@\"</b>\n\n"
        "If you want to stop filling out the questionnaire - send the command - /cancel",
        parse_mode='HTML'
    )


async def karaoke_avatar_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['karaoke_avatar'] = message.photo[0].file_id

    current_state = await state.get_state()
    if current_state == 'NewKaraoke:avatar':
        await NewKaraoke.description.set()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Skip', callback_data='new_karaoke skip description'))
        await message.answer(
            "Now come up with 🗒 <b>DESCRIPTION</b> for your karaoke",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        await message.answer(
            '✅ Success! 🖼 <b>AVATAR</b> updated.',
            reply_markup=keyboards['back_to'],
            parse_mode='HTML'
        )


async def karaoke_avatar_is_invalid(message: types.Message):
    await message.reply(
        "It seems you sent something wrong. "
        "Please send a 🖼 <b>PHOTO</b> to the avatar for your karaoke.\n\n"
        "If you want to stop filling out the questionnaire - send the command - /cancel",
        parse_mode='HTML'
    )


async def karaoke_description_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.html_text
    current_state = await state.get_state()
    if current_state == 'NewKaraoke:description':
        await new_karaoke_command_confirm(message, state)
    else:
        await message.answer(
            '✅ Success! 🗒 <b>DESCRIPTION</b> updated.',
            reply_markup=keyboards['back_to'],
            parse_mode='HTML'
        )


async def karaoke_description_is_invalid(message: types.Message) -> None:
    await message.reply(
        "The maximum length of the 🗒 <b>DESCRIPTION</b> should not exceed 500 characters",
        parse_mode='HTML'
    )


async def new_karaoke_command_confirm(
        message: types.Message,
        state: FSMContext,
        keyboard: InlineKeyboardMarkup = keyboards['confirm']) -> None:

    confirm_text = "<b>CONFIRM THE CREATION OF KARAOKE</b>\n\n"
    async with state.proxy() as data:
        name = data.get('karaoke_name')
        avatar_id = data.get('karaoke_avatar')
        description = data.get('description')

    text = confirm_text + f"<b>NAME</b>: {name}"
    if description is not None:
        text += f"\n🗒 <b>DESCRIPTION</b>: {description}"

    if avatar_id is not None:
        await message.answer_photo(photo=avatar_id, caption=text, reply_markup=keyboard, parse_mode='HTML')
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode='HTML')


async def callback_new_karaoke(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    # button_options = {}  # сделать словарь с кнопками позже

    keyboard = InlineKeyboardMarkup()
    callback_data = callback.data.split(' ')[1:]
    match callback_data:
        case ('create',):
            await callback.message.edit_reply_markup(keyboards['create'])
        case ('create', 'force'):
            await callback.message.delete()

            async with state.proxy() as data:
                message_karaoke_name: types.message = data.get('message_karaoke_name')

            await register_karaoke(state)  # внутри функции state.finish(), обращаться к state.proxy() нужно заранее
            await search_karaoke(message=message_karaoke_name, state=state)
        case ('edit',):
            await callback.message.edit_reply_markup(keyboards['edit'])
        case ('edit', 'name'):
            await NewKaraoke.edit_name.set()
            await callback.message.answer('What <b>NAME</b> would you like for your karaoke?', parse_mode='HTML')
        case ('edit', 'avatar'):
            await NewKaraoke.edit_avatar.set()
            await callback.message.answer('Attach the 🖼 <b>AVATAR</b>  you want', parse_mode='HTML')
        case ('edit', 'description'):
            await NewKaraoke.edit_description.set()
            await callback.message.answer('What 🗒 <b>DESCRIPTION</b> would you like?', parse_mode='HTML')
        case ('skip', 'avatar'):
            await NewKaraoke.description.set()
            await callback.message.edit_reply_markup()  # delete markup
            keyboard.add(InlineKeyboardButton(text='Skip', callback_data='new_karaoke skip description'))
            await callback.message.answer(
                "Now come up with 🗒 <b>DESCRIPTION</b> for your karaoke",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        case ('skip', 'description'):
            await callback.message.edit_reply_markup()  # delete markup
            await new_karaoke_command_confirm(message=callback.message, state=state)
        case ('cancel',):
            await callback.message.edit_reply_markup(keyboards['cancel'])
        case ('cancel', 'force'):
            await callback.message.answer("❌ Create karaoke canceled")
            await callback.message.delete()
            await state.finish()
        case ('back',):
            await callback.message.edit_reply_markup(keyboards['confirm'])
        case ('back', 'confirmation'):
            await callback.message.delete()
            await new_karaoke_command_confirm(message=callback.message, state=state)
        case ('back', 'editing'):
            await callback.message.delete()
            await new_karaoke_command_confirm(message=callback.message, state=state, keyboard=keyboards['edit'])


async def register_karaoke(state: FSMContext):

    async with state.proxy() as data:
        owner: types.User = data.get('owner')
        karaoke_name: str = data.get('karaoke_name')
        avatar_id: str = data.get('karaoke_avatar')
        description: str = data.get('description')

    success_text = "✅ Success! You have created your <b>virtual karaoke</b>!"
    fail_text = "Oops, something went wrong, we are already working on the error"
    try:
        create_karaoke(telegram_id=owner.id, name=karaoke_name, avatar_id=avatar_id, description=description)
        create_karaoke_session(karaoke_name=karaoke_name)
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
        await register_telegram_user(owner)
        await register_karaoke(state)
    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
        await bot.send_message(chat_id=owner.id, text=fail_text)
    else:
        await bot.send_message(chat_id=owner.id, text=success_text, parse_mode='HTML')
    finally:
        await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(new_karaoke_command, commands=['new_karaoke'])

    dp.register_message_handler(
        karaoke_name_registration,
        lambda message: all(c in ascii_letters + digits + '$*&_@' for c in message.text) and len(message.text) <= 20,
        state=[NewKaraoke.name, NewKaraoke.edit_name]
    )

    dp.register_message_handler(
        karaoke_name_is_invalid,
        content_types='any',
        state=[NewKaraoke.name, NewKaraoke.edit_name]
    )

    dp.register_message_handler(
        karaoke_avatar_registration,
        content_types=['photo'],
        state=[NewKaraoke.avatar, NewKaraoke.edit_avatar]
    )

    dp.register_message_handler(
        karaoke_avatar_is_invalid,
        content_types='any',
        state=[NewKaraoke.avatar, NewKaraoke.edit_avatar]
    )

    dp.register_message_handler(
        karaoke_description_registration,
        lambda message: len(message.text) <= 500,
        state=[NewKaraoke.description, NewKaraoke.edit_description]
    )

    dp.register_message_handler(
        karaoke_description_is_invalid,
        content_types='any',
        state=[NewKaraoke.description, NewKaraoke.edit_description]
    )

    dp.register_callback_query_handler(callback_new_karaoke, Text(startswith='new_karaoke'), state='*')
