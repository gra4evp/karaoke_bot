import typing
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import dispatcher, bot
from keyboards import client_keyboards as keyboards
from data_base import sqlite_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, User
from string import ascii_letters, digits
from karaoke_gram.karaoke import Karaoke, KaraokeUser, ready_to_play_karaoke_list,\
    find_first_match_karaoke, add_track_to_queue


class FSMNewKaraoke(StatesGroup):
    karaoke_name = State()
    karaoke_password = State()
    karaoke_avatar = State()


class FSMKaraokeSearch(StatesGroup):
    karaoke_name = State()


class FSMOrderTrack(StatesGroup):
    link = State()


async def start_command(message: types.Message):
    await message.answer("Hello, I'm <b>Moloko</b> - karaoke bot.\n"
                         "I can help you create and manage virtual karaoke and order tracks to your karaoke-man "
                         "(person responsible for turning on the music).\n\n"
                         "You can control me by sending these commands:\n\n"
                         "/new_karaoke - create a new karaoke\n"
                         "/search_karaoke - search for karaoke among existing ones\n"
                         "/order_track - order a music track\n"
                         "/status - show the current status of the user",
                         reply_markup=keyboards,
                         parse_mode='HTML')


async def new_karaoke_command(message: types.Message):
    await message.answer(f"Come up with a <b>name</b> for your karaoke.\n\n"
                         f"To make it easier for users to find you, "
                         f"you can come up with a <b>name</b> similar to your establishment.", parse_mode='HTML')

    await FSMNewKaraoke.karaoke_name.set()


async def karaoke_name_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['karaoke_name'] = message.text

    await message.answer("Now come up with a <b>password</b> for your virtual karaoke.", parse_mode='HTML')
    await FSMNewKaraoke.next()


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
        data['owner_id'] = message.from_user.id
        data['owner_first_name'] = message.from_user.first_name
        data['owner_last_name'] = message.from_user.last_name
        data['owner_username'] = message.from_user.username

    await sqlite_db.sql_add_owner_record(state)

    await message.answer("You have created your <b>virtual karaoke</b>!", parse_mode='HTML')
    await state.finish()


async def search_karaoke_command(message: types.Message):
    await message.answer(f"Enter the <b>name</b> of the virtual karaoke where you plan to perform.", parse_mode='HTML')
    await FSMKaraokeSearch.karaoke_name.set()


async def callback_search_karaoke_command(callback: types.CallbackQuery):
    await callback.answer()
    await search_karaoke_command(callback.message)


async def find_karaoke(message: types.Message, state: FSMContext):

    query = sqlite_db.sql_find_karaoke_record(karaoke_name=message.text)
    if query is not None:
        karaoke_avatar_id, karaoke_name, owner_username = query

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="Subscribe", callback_data=f"subscribe_to {karaoke_name}"))

        await bot.send_photo(message.from_user.id,
                             karaoke_avatar_id,
                             caption=f"<b>Karaoke</b>: {karaoke_name}\n<b>Owner</b>: @{owner_username}",
                             reply_markup=keyboard,
                             parse_mode='HTML')

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
        # Если нет записи о пользователе (нет ни одного караоке в которм он состоит)
        await sqlite_db.sql_add_user_record(user_id, active_karaoke=karaoke_name, karaoke_name=karaoke_name)
    else:
        # Если пользователь уже был в базе, то нужно распарсить список его караоке в которых он учавствует
        # TODO название караоке не должны повторяться, а быть уникальными, нужно будет применять set() или проверка через in
        karaoke_list = query[1].split('; ')
        karaoke_list.append(karaoke_name)
        await sqlite_db.sql_update_user_record(user_id, active_karaoke=karaoke_name, karaoke_list=karaoke_list)

    await callback.answer(f'You have joined "{karaoke_name}" karaoke.\n'
                          f'Now you can order tracks in it.',
                          show_alert=True)


# TODO Ошибка если нажимать статус пользователь который ещё не подписался ни на одно караоке.
async def status_command(message: types.Message, state: FSMContext):
    await state.finish()

    user_info, owner_info = sqlite_db.sql_get_user_status(message.from_user.id)

    if owner_info is None:
        owner_text = ''
    else:
        owner_info = [karaoke_name[0] for karaoke_name in owner_info]
        owner_text = "<b>At the moment you own these karaoke:</b>\n- " + '\n- '.join(owner_info) + '\n\n'

    if user_info is None:
        user_text = ''
    else:
        active_karaoke, karaoke_list = user_info
        karaoke_list = karaoke_list.split('; ')
        user_text = "<b>At the moment you are a member of these karaoke:</b>\n" + '\n- '.join(karaoke_list) + '\n\n'
        user_text += f"<b>Active karaoke:</b>\n{active_karaoke}"

    text = owner_text + user_text

    if text:
        await message.answer(text, parse_mode='HTML')
    else:
        await message.answer('Sorry, there is no information about you yet.')


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


# TODO добавить валидацию на текст в хендлерах имени (сделано), осталось валдиация на длину имени и пароля.
def register_handlers_client(dispatcher: Dispatcher):

    dispatcher.register_callback_query_handler(callback_cancel_command, Text(equals='cancel'))
    dispatcher.register_message_handler(cancel_command, Text(equals='cancel', ignore_case=True), state='*')
    dispatcher.register_message_handler(cancel_command, commands=['cancel'], state='*')

    dispatcher.register_message_handler(status_command, Text(equals="Status", ignore_case=True), state='*')
    dispatcher.register_message_handler(status_command, commands=['status'], state='*')

    dispatcher.register_message_handler(start_command, commands=['start', 'help'])

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

    dispatcher.register_message_handler(order_track_command, commands='order_track')
    dispatcher.register_message_handler(add_link,
                                        Text(startswith=['https://www.youtube.com/watch?v=',
                                                         'https://youtu.be/',
                                                         'https://xminus.me/track/']),
                                        state=FSMOrderTrack.link)
    dispatcher.register_message_handler(state_link_is_invalid, content_types='any', state=FSMOrderTrack.link)

