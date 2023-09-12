from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.visitor_states import OrderTrack
from karaoke_bot.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.models.sqlalchemy_data_utils import get_visitor_karaoke_names, change_selected_karaoke,\
    get_karaoke_owner_id
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, KaraokeNotFoundError, \
    EmptyFieldError, InvalidAccountStateError


async def callback_change_selected_karaoke(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()  # delete markup

    keyboard = InlineKeyboardMarkup()
    match callback.data.split(' '):
        case ['change_selected_karaoke']:
            try:
                karaoke_names = get_visitor_karaoke_names(telegram_id=callback.from_user.id)
            except EmptyFieldError as e:
                print(f"ERROR OCCURRED: {e}")
            else:
                async with state.proxy() as data:
                    karaoke_name = data.get('karaoke_name')

                # TODO продумать как будет выглядит меню кнопок если караоке будет очень много
                text_list = ''
                for index, kname in enumerate(karaoke_names - {karaoke_name}):  # убираем из множества текущее караоке
                    text_list += f'\n– {kname}'
                    button = InlineKeyboardButton(text=kname, callback_data=f'change_selected_karaoke {kname}')

                    if index % 2 == 0:
                        keyboard.add(button)
                    else:
                        keyboard.insert(button)

                keyboard.add(InlineKeyboardButton(text="🔍 Search karaoke", callback_data='search_karaoke'))

                await callback.message.answer(
                    f"Select <b>karaoke</b> where you want to order a track.\n\nYour karaoke list:{text_list}",
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
        case ['change_selected_karaoke', karaoke_name]:
            try:
                change_selected_karaoke(telegram_id=callback.from_user.id, karaoke_name=karaoke_name)
            except KaraokeNotFoundError as e:
                print(f"ERROR OCCURRED: {e}")
            else:  # если удалось поменять selected_karaoke, пробуем узнать owner_id
                try:
                    owner_id = get_karaoke_owner_id(karaoke_name=karaoke_name)
                except EmptyFieldError as e:
                    print(f"ERROR OCCURRED: {e}")
                else:
                    async with state.proxy() as data:
                        data['karaoke_name'] = karaoke_name
                        data['owner_id'] = owner_id

                    keyboard.add(InlineKeyboardButton(text="Change karaoke", callback_data='change_selected_karaoke'))
                    await bot.send_message(
                        chat_id=callback.from_user.id,
                        text=f"Please send a link to the track on YouTube or XMinus\n\n"
                             f"<b>Selected karaoke:</b> {karaoke_name}",
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )


# async def show_my_orders_command(message: types.Message):
#     query = sqlite_db.sql_find_user_record(message.from_user.id)
#     if query is None:
#         await message.answer("Хотите подключиться к караоке?")
#     else:
#         active_karaoke, karaoke_list = query
#         karaoke = find_first_match_karaoke(active_karaoke)
#         if karaoke is None:
#             await message.answer("🗒 You haven't ordered any tracks yet")
#         else:
#             user = karaoke.find_user(message.from_user.id)
#             queue_length = len(user.playlist)
#             if queue_length:
#                 for i in range(queue_length):
#                     keyboard = InlineKeyboardMarkup()
#                     keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
#                     keyboard.insert(InlineKeyboardButton(text="❌ Remove", callback_data=f'rm_track'))
#                     await message.answer(f"{i + 1}. {hlink('Track', user.playlist[i].url)}\n"
#                                          f"Karaoke: {karaoke.name}",
#                                          reply_markup=keyboard,
#                                          parse_mode='HTML')
#             else:
#                 await message.answer("🗒 You haven't ordered any tracks yet")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        callback_change_selected_karaoke,
        Text(startswith='change_selected_karaoke'),
        state=OrderTrack.link
    )

    # dp.register_message_handler(show_my_orders_command, commands=['show_my_orders'])
