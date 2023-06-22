from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.client_states import FSMOrderTrack, FSMKaraokeSearch, FSMNewKaraoke
from karaoke_bot.create_bot import bot
from data_base import sqlite_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hlink
from string import ascii_letters, digits
from karaoke_bot.karaoke_gram.karaoke import find_first_match_karaoke, add_track_to_queue


async def new_karaoke_command(message: types.Message):
    await message.answer(f"Come up with a <b>name</b> for your karaoke.\n\n"
                         f"To make it easier for users to find you, "
                         f"you can come up with a <b>name</b> similar to your establishment.", parse_mode='HTML')

    await FSMNewKaraoke.karaoke_name.set()


async def karaoke_name_registration(message: types.Message, state: FSMContext):

    karaoke_name = message.text

    if not sqlite_db.karaoke_is_exists(karaoke_name):
        async with state.proxy() as data:
            data['karaoke_name'] = karaoke_name

        await message.answer("Now come up with a <b>password</b> for your virtual karaoke.", parse_mode='HTML')
        await FSMNewKaraoke.next()
    else:
        await message.reply("🔒 Sorry, this <b>name</b> is already taken.", parse_mode='HTML')


async def state_karaoke_name_is_invalid(message: types.Message):
    await message.reply("The <b>karaoke name</b> must be presented in text and contain't any punctuation marks, "
                        "except for: <b>\"$*&_@\"</b>\n\n"
                        "If you want to stop filling out the questionnaire - send the command - /cancel",
                        parse_mode='HTML')


async def karaoke_password_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['karaoke_password'] = message.text

    await message.answer("Now send the photo you would like to set as your avatar")
    await FSMNewKaraoke.next()


async def state_karaoke_password_is_invalid(message: types.Message):
    await message.reply("The <b>karaoke password</b> must be presented in text and contain't any punctuation marks, "
                        "except for: <b>\"$*&_@\"</b>\n\n"
                        "If you want to stop filling out the questionnaire - send the command - /cancel",
                        parse_mode='HTML')


async def karaoke_avatar_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['karaoke_avatar'] = message.photo[0].file_id
    await owner_data_registration(message, state)


async def state_karaoke_avatar_is_invalid(message: types.Message):
    await message.reply("It seems you sent something wrong. "
                        "Please send a <b>photo</b> to the avatar for your karaoke.\n\n"
                        "If you want to stop filling out the questionnaire - send the command - /cancel",
                        parse_mode='HTML')


async def owner_data_registration(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        karaoke_name = data.get('karaoke_name')
        password = data.get('karaoke_password')
        avatar_id = data.get('karaoke_avatar')

    onwer_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    await sqlite_db.sql_add_owner_record(karaoke_name, password, avatar_id, onwer_id, first_name, last_name, username)

    await message.answer("You have created your <b>virtual karaoke</b>!", parse_mode='HTML')
    await state.finish()


async def search_karaoke_command(message: types.Message):
    await message.answer(f"Enter the <b>name</b> of the virtual karaoke where you plan to perform.", parse_mode='HTML')
    await FSMKaraokeSearch.karaoke_name.set()


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
        await message.reply("Oops, there is no such karaoke yet.\n\n"
                            "Try to get the <b>name</b> from the administrator of the institution where you are.",
                            parse_mode='HTML')


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
    # Если нет записи о пользователе, то переходим в хендлер_callback для команды /search_karaoke или /cancel
    query = sqlite_db.sql_find_user_record(message.from_user.id)
    if query is not None:

        active_karaoke, karaoke_list = query
        owner_id = sqlite_db.sql_find_owner_id(karaoke_name=active_karaoke)

        async with state.proxy() as data:
            data['active_karaoke'] = active_karaoke
            data['owner_id'] = owner_id

        await message.answer("Send a <b>link</b> to the track on YouTube", parse_mode='HTML')
        await FSMOrderTrack.link.set()

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
    await message.reply("It seems you sent something wrong."
                        "Please send a <b>link</b> to the track on YouTube\n\n"
                        "The <b>link</b> must be in the format:\n"
                        "✅ - https://youtu.be/\n"
                        "✅ - https://www.youtube.com/",
                        parse_mode='HTML')


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
        state=FSMNewKaraoke.karaoke_name)

    dispatcher.register_message_handler(
        karaoke_password_registration,
        lambda message: all(c in ascii_letters + digits + '$*&_@' for c in message.text) and len(message.text) <= 20,
        state=FSMNewKaraoke.karaoke_password)
    dispatcher.register_message_handler(state_karaoke_password_is_invalid,
                                        content_types='any',
                                        state=FSMNewKaraoke.karaoke_password)

    dispatcher.register_message_handler(karaoke_avatar_registration,
                                        content_types=['photo'],
                                        state=FSMNewKaraoke.karaoke_avatar)
    dispatcher.register_message_handler(state_karaoke_avatar_is_invalid,
                                        content_types='any',
                                        state=FSMNewKaraoke.karaoke_avatar)

    dispatcher.register_message_handler(search_karaoke_command, commands=['search_karaoke'])
    dispatcher.register_callback_query_handler(callback_search_karaoke_command, Text(equals='search_karaoke'))

    dispatcher.register_message_handler(find_karaoke, state=FSMKaraokeSearch.karaoke_name)
    dispatcher.register_message_handler(state_karaoke_name_is_invalid, content_types='any',
                                        state=[FSMKaraokeSearch.karaoke_name, FSMNewKaraoke.karaoke_name])

    dispatcher.register_callback_query_handler(callback_subscribe_to_karaoke, Text(startswith='subscribe_to'))

    dispatcher.register_message_handler(order_track_command, commands=['order_track'])
    dispatcher.register_message_handler(add_link,
                                        Text(startswith=['https://www.youtube.com/watch?v=',
                                                         'https://youtu.be/',
                                                         'https://xminus.me/track/']),
                                        state=FSMOrderTrack.link)
    dispatcher.register_message_handler(state_link_is_invalid, content_types='any', state=FSMOrderTrack.link)

    dispatcher.register_message_handler(show_my_orders_command, commands=['show_my_orders'])

