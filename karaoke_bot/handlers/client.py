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
from karaoke_bot.models.sqlalchemy_data_utils import karaoke_not_exists, create_karaoke


async def new_karaoke_command(message: types.Message):
    await message.answer(f"Come up with a <b>name</b> for your karaoke.\n\n"
                         f"To make it easier for users to find you, "
                         f"you can come up with a <b>name</b> similar to your establishment.", parse_mode='HTML')

    await NewKaraoke.name.set()


async def karaoke_name_registration(message: types.Message, state: FSMContext):
    karaoke_name = message.text
    if karaoke_not_exists(karaoke_name):
        async with state.proxy() as data:
            data['karaoke_name'] = karaoke_name

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='Skip', callback_data='karaoke_registration_skip avatar'))
        await message.answer(
            "Now send the photo you want to set as your karaoke avatar.",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        await NewKaraoke.avatar.set()
    else:
        await message.reply("🔒 Sorry, this <b>name</b> is already taken.", parse_mode='HTML')


async def state_karaoke_name_is_invalid(message: types.Message):
    await message.reply(
        "The <b>karaoke name</b> must be presented in text and contain't any punctuation marks, "
        "except for: <b>\"$*&_@\"</b>\n\n"
        "If you want to stop filling out the questionnaire - send the command - /cancel",
        parse_mode='HTML'
    )


# async def karaoke_password_registration(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['karaoke_password'] = message.text
#
#     keyboard = InlineKeyboardMarkup()
#     keyboard.add(InlineKeyboardButton(text='Skip', callback_data='karaoke_registration_skip avatar'))
#     await message.answer("Now send the photo you would like to set as your avatar", reply_markup=keyboard)
#     await NewKaraoke.next()


# async def state_karaoke_password_is_invalid(message: types.Message):
#     await message.reply(
#         "The <b>karaoke password</b> must be presented in text and contain't any punctuation marks, "
#         "except for: <b>\"$*&_@\"</b>\n\n"
#         "If you want to stop filling out the questionnaire - send the command - /cancel",
#         parse_mode='HTML'
#     )


async def karaoke_avatar_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['karaoke_avatar'] = message.photo[0].file_id

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Skip', callback_data='karaoke_registration_skip description'))
    await message.answer("Now come up with descriptions for your karaoke", reply_markup=keyboard)
    await NewKaraoke.description.set()


async def state_karaoke_avatar_is_invalid(message: types.Message):
    await message.reply(
        "It seems you sent something wrong. "
        "Please send a <b>photo</b> to the avatar for your karaoke.\n\n"
        "If you want to stop filling out the questionnaire - send the command - /cancel",
        parse_mode='HTML'
    )


async def karaoke_description_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.html_text
    await new_karaoke_command_confirm(message, state)


async def state_karaoke_description_is_invalid(message: types.Message) -> None:
    await message.reply(
        "The maximum length of the <b>description</b> should not exceed 500 characters",
        parse_mode='HTML'
    )


async def new_karaoke_command_confirm(message: types.Message, state: FSMContext) -> None:
    confirm_text = "<b>CONFIRM THE CREATION OF KARAOKE</b>"
    async with state.proxy() as data:
        name = data.get('karaoke_name')
        avatar_id = data.get('karaoke_avatar')
        description = data.get('description')

    text = confirm_text + f"\nName: {name}"
    if description is not None:
        text += f"\nDescription: {description}"

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('✅ Confirm and Create', callback_data='new_karaoke create'))
    keyboard.insert(InlineKeyboardButton('✏️ Edit', callback_data='new_karaoke edit'))
    keyboard.add(InlineKeyboardButton('❌ Delete', callback_data='new_karaoke delete'))

    if avatar_id is not None:
        await message.answer_photo(photo=avatar_id, caption=text, reply_markup=keyboard, parse_mode='HTML')
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode='HTML')

    await state.finish()


async def callback_new_karaoke_confirm(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    callback_data = callback.data.split(' ')
    match callback_data:
        case _, cmd, *arg:  # если 2 аргумента, то arg = []
            keyboard = InlineKeyboardMarkup()
            if arg:
                arg = arg[0]
            match cmd:
                case 'create':
                    if arg == 'force':
                        await callback.answer("✅ Karaoke successfully created!", show_alert=True)
                        await callback.message.delete()
                        await owner_data_registration(message=callback.message, state=state)
                    else:
                        keyboard.add(
                            InlineKeyboardButton("✅ Create", callback_data='new_karaoke create force'),
                            InlineKeyboardButton("<< Back", callback_data='new_karaoke back')
                        )
                        await callback.message.edit_reply_markup(keyboard)
                case 'edit':
                    if arg == 'text':
                        pass
                    if arg == 'avatar':
                        pass
                    if arg == 'description':
                        pass
                    else:
                        keyboard.add(InlineKeyboardButton("💬 Edit karaoke name", callback_data='new_karaoke edit text'))
                        keyboard.insert(InlineKeyboardButton("🖼 Edit avatar", callback_data='new_karaoke edit avatar'))
                        keyboard.add(
                            InlineKeyboardButton("🗓 Edit description", callback_data='new_karaoke edit description'))
                        keyboard.add(InlineKeyboardButton("<< Back", callback_data='new_karaoke back'))
                        await callback.message.edit_reply_markup(keyboard)
                case 'cancel':
                    if arg == 'force':
                        await callback.message.answer("❌ Create karaoke canceled")
                        await callback.message.delete()
                        await state.finish()
                    else:
                        keyboard.add(
                            InlineKeyboardButton("❌ Cancel", callback_data='new_karaoke cancel force'),
                            InlineKeyboardButton("<< Back", callback_data='new_karaoke back')
                        )
                        await callback.message.edit_reply_markup(keyboard)
                case 'back':
                    keyboard.add(InlineKeyboardButton('✅ Confirm and Create', callback_data='new_karaoke create'))
                    keyboard.insert(InlineKeyboardButton('✏️ Edit', callback_data='new_karaoke edit'))
                    keyboard.add(InlineKeyboardButton('❌ Cancel', callback_data='new_karaoke cancel'))
                    await callback.message.edit_reply_markup(keyboard)


async def owner_data_registration(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        karaoke_name = data.get('karaoke_name')
        avatar_id = data.get('karaoke_avatar')
        description = data.get('description')

    try:
        create_karaoke(
            telegram_id=message.from_user.id,
            name=karaoke_name,
            avatar_id=avatar_id,
            description=description
        )
    except Exception as e:
        print(f"Error occurred: {e}")
        await message.answer("Oops, something went wrong, we are already working on the error")
    else:
        await message.answer("You have created your <b>virtual karaoke</b>!", parse_mode='HTML')
    finally:
        await state.finish()


async def search_karaoke_command(message: types.Message):
    await message.answer(f"Enter the <b>name</b> of the virtual karaoke where you plan to perform.", parse_mode='HTML')
    await KaraokeSearch.name.set()


async def callback_search_karaoke_command(callback: types.CallbackQuery):
    await callback.answer()
    await search_karaoke_command(callback.message)


async def find_karaoke(message: types.Message, state: FSMContext):

    karaoke_name = message.text
    user_id = message.from_user.id

    query = sqlite_db.sql_find_karaoke_record(karaoke_name)
    if query is not None:  # если есть такое караоке
        avatar_id, owner_username = query

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="Subscribe", callback_data=f"subscribe_to {karaoke_name}"))
        caption = f"<b>Karaoke</b>: {karaoke_name}\n<b>Owner</b>: @{owner_username}"

        user_info = sqlite_db.sql_find_user_record(message.from_user.id)
        if user_info is not None:  # если есть такой пользователь

            active_karaoke, karaoke_list = user_info
            if karaoke_name in karaoke_list.split('; '):  # если пользователь уже подписан
                keyboard = None
                caption += "\n\n✅ You have already subscribed!"

        await bot.send_photo(user_id, avatar_id, caption=caption, reply_markup=keyboard, parse_mode='HTML')
        await state.finish()
    else:
        await message.reply(
            "Oops, there is no such karaoke yet.\n\n"
            "Try to get the <b>name</b> from the administrator of the institution where you are.",
            parse_mode='HTML'
        )


async def callback_subscribe_to_karaoke(callback: types.CallbackQuery):

    karaoke_name = callback.data.split(' ')[-1]
    user_id = callback.from_user.id

    # удаление inline кнопки после нажатия
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=callback.message.message_id)

    query = sqlite_db.sql_find_user_record(user_id)
    if query is None:
        # Если нет записи о пользователе (нет ни одного караоке в котором он состоит)
        await sqlite_db.sql_add_user_record(user_id, active_karaoke=karaoke_name, karaoke_name=karaoke_name)
    else:
        # Если пользователь уже был в базе, то нужно распарсить список его караоке в которых он учавствует
        karaoke_list = query[1].split('; ')
        karaoke_list.append(karaoke_name)
        await sqlite_db.sql_update_user_record(user_id, active_karaoke=karaoke_name, karaoke_list=karaoke_list)

    await callback.answer(f'✅ You have joined "{karaoke_name}" karaoke.\n'
                          f'Now you can order tracks in it.',
                          show_alert=True)


async def order_track_command(message: types.Message, state: FSMContext):
    # Если нет записи о пользователе, то перехходим в хендлер_callback для команды /search_karaoke или /cancel
    query = sqlite_db.sql_find_user_record(message.from_user.id)
    if query is not None:

        active_karaoke, karaoke_list = query
        owner_id = sqlite_db.sql_find_owner_id(karaoke_name=active_karaoke)

        async with state.proxy() as data:
            data['active_karaoke'] = active_karaoke
            data['owner_id'] = owner_id

        await message.answer("Send a <b>link</b> to the track on YouTube", parse_mode='HTML')
        await OrderTrack.link.set()

    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="✅ Yes", callback_data='search_karaoke'))
        keyboard.insert(InlineKeyboardButton(text="❌ No", callback_data='cancel'))
        await message.answer("You don't have an active karaoke yet where you could order music.\n\n"
                             "Go to karaoke search?", reply_markup=keyboard, parse_mode='HTML')


async def add_link(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        active_karaoke = data.get('active_karaoke')
        owner_id = int(data.get('owner_id'))

    add_track_to_queue(user=message.from_user, karaoke_name=active_karaoke, owner_id=owner_id, track_url=message.text)

    # Записываем в базу кто поставил какой трек.
    await sqlite_db.sql_add_track_record(user_id=message.from_user.id, active_karaoke=active_karaoke, link=message.text)
    await message.answer("✅ Your track has been added to the queue!")
    await state.finish()


async def state_link_is_invalid(message: types.Message):
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


def register_handlers_client(dispatcher: Dispatcher):
    dispatcher.register_message_handler(new_karaoke_command, commands=['new_karaoke'])
    # Фильтр для валидации текста
    dispatcher.register_message_handler(
        karaoke_name_registration,
        lambda message: all(c in ascii_letters + digits + '$*&_@' for c in message.text) and len(message.text) <= 20,
        state=NewKaraoke.name
    )

    # dispatcher.register_message_handler(
    #     karaoke_password_registration,
    #     lambda message: all(c in ascii_letters + digits + '$*&_@' for c in message.text) and len(message.text) <= 20,
    #     state=NewKaraoke.password)
    # dispatcher.register_message_handler(state_karaoke_password_is_invalid,
    #                                     content_types='any',
    #                                     state=NewKaraoke.password)

    dispatcher.register_message_handler(karaoke_avatar_registration, content_types=['photo'], state=NewKaraoke.avatar)
    dispatcher.register_message_handler(state_karaoke_avatar_is_invalid, content_types='any', state=NewKaraoke.avatar)

    dispatcher.register_message_handler(
        karaoke_description_registration,
        lambda message: len(message.text) <= 500,
        state=NewKaraoke.description
    )
    dispatcher.register_message_handler(
        state_karaoke_description_is_invalid,
        content_types='any',
        state=NewKaraoke.description
    )

    dispatcher.register_callback_query_handler(callback_new_karaoke_confirm, Text(startswith='new_karaoke'))

    dispatcher.register_message_handler(search_karaoke_command, commands=['search_karaoke'])
    dispatcher.register_callback_query_handler(callback_search_karaoke_command, Text(equals='search_karaoke'))

    dispatcher.register_message_handler(find_karaoke, state=KaraokeSearch.name)
    dispatcher.register_message_handler(state_karaoke_name_is_invalid, content_types='any',
                                        state=[KaraokeSearch.name, NewKaraoke.name])

    dispatcher.register_callback_query_handler(callback_subscribe_to_karaoke, Text(startswith='subscribe_to'))

    dispatcher.register_message_handler(order_track_command, commands=['order_track'])
    dispatcher.register_message_handler(add_link,
                                        Text(startswith=['https://www.youtube.com/watch?v=',
                                                         'https://youtu.be/',
                                                         'https://xminus.me/track/']),
                                        state=OrderTrack.link)
    dispatcher.register_message_handler(state_link_is_invalid, content_types='any', state=OrderTrack.link)

    dispatcher.register_message_handler(show_my_orders_command, commands=['show_my_orders'])

