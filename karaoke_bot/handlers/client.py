from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.client_states import OrderTrack, KaraokeSearch, NewKaraoke
from karaoke_bot.create_bot import bot
from data_base import sqlite_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hlink
from string import ascii_letters, digits
from karaoke_bot.karaoke_gram.karaoke import find_first_match_karaoke, add_track_to_queue
from karaoke_bot.models.sqlalchemy_data_utils import create_or_update_telegram_profile, karaoke_not_exists,\
    create_karaoke, find_karaoke, subscribe_to_karaoke, has_active_karaoke, create_karaoke_session
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, KaraokeNotFoundError
from karaoke_bot.models.sqlalchemy_models_without_polymorph import AlchemySession, Karaoke


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

        current_state = await state.get_state()
        keyboard = InlineKeyboardMarkup()
        if current_state == 'NewKaraoke:name':
            keyboard.add(InlineKeyboardButton(text='Skip', callback_data='new_karaoke skip avatar'))
            await message.answer(
                "Now send the 🖼 <b>PHOTO</b> you want to set as your karaoke avatar.",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            await NewKaraoke.avatar.set()
        else:
            keyboard.add(InlineKeyboardButton("<< Back to confirmation", callback_data='new_karaoke back confirmation'))
            keyboard.insert(InlineKeyboardButton("<< Back to editing", callback_data='new_karaoke back editing'))
            await message.answer('✅ Success! <b>NAME</b> updated.', reply_markup=keyboard, parse_mode='HTML')
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
    keyboard = InlineKeyboardMarkup()
    if current_state == 'NewKaraoke:avatar':
        await NewKaraoke.description.set()
        keyboard.add(InlineKeyboardButton(text='Skip', callback_data='new_karaoke skip description'))
        await message.answer(
            "Now come up with 🗓 <b>DESCRIPTION</b> for your karaoke",
            reply_markup=keyboard,
            parse_mode='HTML')
    else:
        keyboard.add(InlineKeyboardButton("<< Back to confirmation", callback_data='new_karaoke back confirmation'))
        keyboard.insert(InlineKeyboardButton("<< Back to editing", callback_data='new_karaoke back editing'))
        await message.answer('✅ Success! 🖼 <b>AVATAR</b> updated.', reply_markup=keyboard, parse_mode='HTML')


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
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("<< Back to confirmation", callback_data='new_karaoke back confirmation'))
        keyboard.insert(InlineKeyboardButton("<< Back to editing", callback_data='new_karaoke back editing'))
        await message.answer('✅ Success! 🗓 <b>DESCRIPTION</b> updated.', reply_markup=keyboard, parse_mode='HTML')


async def karaoke_description_is_invalid(message: types.Message) -> None:
    await message.reply(
        "The maximum length of the 🗓 <b>DESCRIPTION</b> should not exceed 500 characters",
        parse_mode='HTML'
    )


async def new_karaoke_command_confirm(
        message: types.Message,
        state: FSMContext,
        keyboard: InlineKeyboardMarkup | None = None) -> None:

    confirm_text = "<b>CONFIRM THE CREATION OF KARAOKE</b>"
    async with state.proxy() as data:
        name = data.get('karaoke_name')
        avatar_id = data.get('karaoke_avatar')
        description = data.get('description')

    text = confirm_text + f"\nNAME: {name}"
    if description is not None:
        text += f"\n🗓 <b>DESCRIPTION</b>: {description}"

    if keyboard is None:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('✅ Confirm and Create', callback_data='new_karaoke create'))
        keyboard.insert(InlineKeyboardButton('✏️ Edit', callback_data='new_karaoke edit'))
        keyboard.add(InlineKeyboardButton('❌ Delete', callback_data='new_karaoke delete'))

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
            keyboard.add(
                InlineKeyboardButton("✅ Create", callback_data='new_karaoke create force'),
                InlineKeyboardButton("<< Back", callback_data='new_karaoke back')
            )
            await callback.message.edit_reply_markup(keyboard)
        case ('create', 'force'):
            await callback.answer("✅ Karaoke successfully created!", show_alert=True)
            await callback.message.delete()
            await register_karaoke(state)
        case ('edit',):
            keyboard.add(InlineKeyboardButton("💬 Edit name", callback_data='new_karaoke edit name'))
            keyboard.insert(InlineKeyboardButton("🖼 Edit avatar", callback_data='new_karaoke edit avatar'))
            keyboard.add(InlineKeyboardButton("🗓 Edit description", callback_data='new_karaoke edit description'))
            keyboard.add(InlineKeyboardButton("<< Back", callback_data='new_karaoke back'))
            await callback.message.edit_reply_markup(keyboard)
        case ('edit', 'name'):
            await NewKaraoke.edit_name.set()
            await callback.message.answer('What <b>NAME</b> would you like for your karaoke?', parse_mode='HTML')
        case ('edit', 'avatar'):
            await NewKaraoke.edit_avatar.set()
            await callback.message.answer('Attach the 🖼 <b>AVATAR</b>  you want', parse_mode='HTML')
        case ('edit', 'description'):
            await NewKaraoke.edit_description.set()
            await callback.message.answer('What 🗓 <b>DESCRIPTION</b> would you like?', parse_mode='HTML')
        case ('skip', 'avatar'):
            await NewKaraoke.description.set()
            await callback.message.edit_reply_markup()  # delete markup
            keyboard.add(InlineKeyboardButton(text='Skip', callback_data='new_karaoke skip description'))
            await callback.message.answer(
                "Now come up with 🗓 <b>DESCRIPTION</b> for your karaoke",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        case ('skip', 'description'):
            await callback.message.edit_reply_markup()  # delete markup
            await new_karaoke_command_confirm(message=callback.message, state=state)
        case ('cancel',):
            keyboard.add(
                InlineKeyboardButton("❌ Cancel", callback_data='new_karaoke cancel force'),
                InlineKeyboardButton("<< Back", callback_data='new_karaoke back')
            )
            await callback.message.edit_reply_markup(keyboard)
        case ('cancel', 'force'):
            await callback.message.answer("❌ Create karaoke canceled")
            await callback.message.delete()
            await state.finish()
        case ('back',):
            keyboard.add(InlineKeyboardButton('✅ Confirm and Create', callback_data='new_karaoke create'))
            keyboard.insert(InlineKeyboardButton('✏️ Edit', callback_data='new_karaoke edit'))
            keyboard.add(InlineKeyboardButton('❌ Cancel', callback_data='new_karaoke cancel'))
            await callback.message.edit_reply_markup(keyboard)
        case ('back', 'confirmation'):
            await callback.message.delete()
            await new_karaoke_command_confirm(message=callback.message, state=state)
        case ('back', 'editing'):
            await callback.message.delete()
            keyboard.add(InlineKeyboardButton("💬 Edit name", callback_data='new_karaoke edit name'))
            keyboard.insert(InlineKeyboardButton("🖼 Edit avatar", callback_data='new_karaoke edit avatar'))
            keyboard.add(InlineKeyboardButton("🗓 Edit description", callback_data='new_karaoke edit description'))
            keyboard.add(InlineKeyboardButton("<< Back", callback_data='new_karaoke back'))
            await new_karaoke_command_confirm(message=callback.message, state=state, keyboard=keyboard)


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
        try:
            create_or_update_telegram_profile(user=owner)
            create_karaoke(telegram_id=owner.id, name=karaoke_name, avatar_id=avatar_id, description=description)
            create_karaoke_session(karaoke_name=karaoke_name)
            await bot.send_message(chat_id=owner.id, text=success_text, parse_mode='HTML')
        except Exception:
            raise  # Raising the exception above

    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
        await bot.send_message(chat_id=owner.id, text=fail_text)
    else:
        await bot.send_message(chat_id=owner.id, text=success_text, parse_mode='HTML')
    finally:
        await state.finish()


async def search_karaoke_command(message: types.Message):
    await message.answer(f"Enter the <b>NAME</b> of the virtual karaoke where you plan to perform.", parse_mode='HTML')
    await KaraokeSearch.name.set()


async def callback_search_karaoke_command(callback: types.CallbackQuery):
    await callback.answer()
    await search_karaoke_command(callback.message)


async def search_karaoke(message: types.Message, state: FSMContext):
    with AlchemySession() as session:
        karaoke = session.query(Karaoke).filter_by(name=message.text).first()

        if karaoke is not None:  # если есть такое караоке
            avatar_id = karaoke.avatar_id
            description = karaoke.description
            owner_username = karaoke.owner.account.telegram_profile.username

            caption = f"<b>Karaoke</b>: {karaoke.name}\n<b>Owner</b>: @{owner_username}\n"

            if description is not None:
                caption += description

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text="Subscribe", callback_data=f"subscribe_to {karaoke.name}"))

            for visitor in karaoke.subscribers:
                if message.from_user.id == visitor.account.telegram_profile.id:
                    keyboard = None
                    caption += "\n\n✅ You have already subscribed!"

            if avatar_id is not None:
                await bot.send_photo(
                    chat_id=message.from_user.id,
                    photo=avatar_id,
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await message.answer(caption, reply_markup=keyboard, parse_mode='HTML')
            await state.finish()
        else:
            await message.reply(
                "Oops, there is no such karaoke yet.\n\n"
                "Try to get the <b>NAME</b> from the administrator of the institution where you are.",
                parse_mode='HTML'
            )


async def callback_subscribe_to_karaoke(callback: types.CallbackQuery):

    karaoke_name = callback.data.split(' ')[-1]
    user_id = callback.from_user.id

    await callback.message.edit_reply_markup()  # delete markup
    try:
        subscribe_to_karaoke(telegram_id=user_id, karaoke_name=karaoke_name)
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
        try:
            create_or_update_telegram_profile(user=callback.from_user)
            subscribe_to_karaoke(telegram_id=user_id, karaoke_name=karaoke_name)
        except Exception:
            raise
    except KaraokeNotFoundError as e:
        print(f"ERROR OCCURRED: {e.args}")
        await callback.answer(text=e.args[0])
    else:
        await callback.message.answer("✅ Success! You have subscribed!")
        await order_track_command(message=callback.message, user_id=callback.from_user.id)


async def order_track_command(message: types.Message, user_id=None):
    if user_id is None:
        user_id = message.from_user.id

    if has_active_karaoke(telegram_id=user_id):
        await bot.send_message(chat_id=user_id, text="Please send a link to the track", parse_mode='HTML')
        await OrderTrack.link.set()
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="✅ Yes", callback_data='search_karaoke'))
        keyboard.insert(InlineKeyboardButton(text="❌ No", callback_data='cancel'))
        await bot.send_message(
            chat_id=user_id,
            text="You don't have an active karaoke yet where you could order music.\n\nGo to karaoke search?",
            reply_markup=keyboard,
            parse_mode='HTML'
        )


async def add_link(message: types.Message, state: FSMContext):

    # add_track_to_queue(user=message.from_user, karaoke_name=active_karaoke, owner_id=owner_id, track_url=message.text)

    # Записываем в базу кто поставил какой трек.
    # await sqlite_db.sql_add_track_record(user_id=message.from_user.id, active_karaoke=active_karaoke, link=message.text)
    await message.answer("✅ Your track has been added to the queue!")
    await state.finish()


async def link_is_invalid(message: types.Message):
    await message.reply(
        "It seems you sent something wrong."
        "Please send a <b>link</b> to the track on YouTube\n\n"
        "The <b>link</b> must be in the format:\n"
        "✅ - https://youtu.be/\n"
        "✅ - https://www.youtube.com/",
        parse_mode='HTML'
    )


async def show_my_orders_command(message: types.Message):
    query = sqlite_db.sql_find_user_record(message.from_user.id)
    if query is None:
        await message.answer("Хотите подключиться к караоке?")
    else:
        active_karaoke, karaoke_list = query
        karaoke = find_first_match_karaoke(active_karaoke)
        if karaoke is None:
            await message.answer("🗒 You haven't ordered any tracks yet")
        else:
            user = karaoke.find_user(message.from_user.id)
            queue_length = len(user.playlist)
            if queue_length:
                for i in range(queue_length):
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
                    keyboard.insert(InlineKeyboardButton(text="❌ Remove", callback_data=f'rm_track'))
                    await message.answer(f"{i + 1}. {hlink('Track', user.playlist[i].url)}\n"
                                         f"Karaoke: {karaoke.name}",
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
            else:
                await message.answer("🗒 You haven't ordered any tracks yet")


def register_client_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(new_karaoke_command, commands=['new_karaoke'])
    # Фильтр для валидации текста
    dispatcher.register_message_handler(
        karaoke_name_registration,
        lambda message: all(c in ascii_letters + digits + '$*&_@' for c in message.text) and len(message.text) <= 20,
        state=[NewKaraoke.name, NewKaraoke.edit_name]
    )

    dispatcher.register_message_handler(
        karaoke_avatar_registration,
        content_types=['photo'],
        state=[NewKaraoke.avatar, NewKaraoke.edit_avatar]
    )
    dispatcher.register_message_handler(
        karaoke_avatar_is_invalid,
        content_types='any',
        state=[NewKaraoke.avatar, NewKaraoke.edit_avatar]
    )

    dispatcher.register_message_handler(
        karaoke_description_registration,
        lambda message: len(message.text) <= 500,
        state=[NewKaraoke.description, NewKaraoke.edit_description]
    )
    dispatcher.register_message_handler(
        karaoke_description_is_invalid,
        content_types='any',
        state=[NewKaraoke.description, NewKaraoke.edit_description]
    )

    dispatcher.register_callback_query_handler(callback_new_karaoke, Text(startswith='new_karaoke'), state='*')

    dispatcher.register_message_handler(search_karaoke_command, commands=['search_karaoke'])
    dispatcher.register_callback_query_handler(callback_search_karaoke_command, Text(equals='search_karaoke'))

    dispatcher.register_message_handler(search_karaoke, state=KaraokeSearch.name)
    dispatcher.register_message_handler(
        karaoke_name_is_invalid,
        content_types='any',
        state=[KaraokeSearch.name, NewKaraoke.name]
    )

    dispatcher.register_callback_query_handler(callback_subscribe_to_karaoke, Text(startswith='subscribe_to'))
    dispatcher.register_message_handler(order_track_command, commands=['order_track'])
    dispatcher.register_message_handler(
        add_link,
        Text(startswith=[
            'https://www.youtube.com/watch?v=',
            'https://youtu.be/',
            'https://xminus.me/track/'
        ]),
        state=OrderTrack.link
    )
    dispatcher.register_message_handler(link_is_invalid, content_types='any', state=OrderTrack.link)

    dispatcher.register_message_handler(show_my_orders_command, commands=['show_my_orders'])

