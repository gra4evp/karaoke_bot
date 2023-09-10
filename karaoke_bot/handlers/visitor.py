from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.client_states import OrderTrack, KaraokeSearch
from karaoke_bot.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hlink
from .other import register_telegram_user
from karaoke_bot.karaoke_gram.karaoke import find_first_match_karaoke, add_track_to_queue
from karaoke_bot.models.sqlalchemy_data_utils import create_or_update_telegram_profile, subscribe_to_karaoke,\
    get_selected_karaoke_data, add_performance_to_visitor
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, KaraokeNotFoundError, \
    EmptyFieldError, InvalidAccountStateError
from karaoke_bot.models.sqlalchemy_models_without_polymorph import AlchemySession, Karaoke
from utils import format_subscribers_count


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
            subscribers = karaoke.subscribers

            caption = f"<b>Karaoke</b>: {karaoke.name}\n" \
                      f"<b>Owner</b>: @{owner_username}\n" \
                      f"<b>Subscribers</b>: {format_subscribers_count(len(subscribers))}\n\n"

            if description is not None:
                caption += description

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text="Subscribe", callback_data=f"subscribe_to {karaoke.name}"))

            for visitor in subscribers:
                if message.from_user.id == visitor.account.telegram_profile.id:
                    keyboard = None
                    caption += "\n\n✅ You have already subscribed!"
                    break

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


async def callback_subscribe_to_karaoke(callback: types.CallbackQuery, state: FSMContext):

    karaoke_name = callback.data.split(' ')[-1]
    user_id = callback.from_user.id

    await callback.message.edit_reply_markup()  # delete markup
    try:
        subscribe_to_karaoke(telegram_id=user_id, karaoke_name=karaoke_name)
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
        await register_telegram_user(callback.from_user)
        await callback_subscribe_to_karaoke(callback, state)
    except KaraokeNotFoundError as e:
        print(f"ERROR OCCURRED: {e.args}")
        await callback.message.answer(text=e.args[0])
    else:
        await callback.message.answer("✅ Success! You have subscribed!")
        current_state = await state.get_state()
        await order_track_command(callback.message, state, callback.from_user.id)


async def order_track_command(message: types.Message, state: FSMContext, user_id=None):
    if user_id is None:
        user_id = message.from_user.id

    try:
        karaoke_name, owner_id = get_selected_karaoke_data(telegram_id=user_id)
    except (EmptyFieldError, InvalidAccountStateError) as e:
        print(f"ERROR OCCURRED: {e}")

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="✅ Yes", callback_data='search_karaoke'))
        keyboard.insert(InlineKeyboardButton(text="❌ No", callback_data='cancel'))
        await bot.send_message(
            chat_id=user_id,
            text="You have not chosen any karaoke where you can order music.\n\nGo to karaoke search?",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
        await register_telegram_user(message.from_user)
        await order_track_command(message, state, user_id)
    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
    else:
        await OrderTrack.link.set()
        async with state.proxy() as data:
            data['karaoke_name'] = karaoke_name
            data['owner_id'] = owner_id
        await bot.send_message(
            chat_id=user_id,
            text=f"Please send a link to the track on YouTube or XMinus\n\n"
                 f"Karaoke: <b>{karaoke_name}</b>",
            parse_mode='HTML'
        )


async def add_link(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        karaoke_name = data.get('karaoke_name')
        owner_id = data.get('owner_id')

    try:
        add_performance_to_visitor(telegram_id=message.from_user.id, track_url=message.text)
    except (EmptyFieldError, InvalidAccountStateError) as e:
        print(f"ERROR OCCURRED: {e}")
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
    else:
        add_track_to_queue(user=message.from_user, karaoke_name=karaoke_name, owner_id=owner_id, track_url=message.text)
        await message.answer("✅ Your track has been added to the queue!")
    finally:
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


def register_visitor_handlers(dp: Dispatcher):
    dp.register_message_handler(search_karaoke_command, commands=['search_karaoke'])

    dp.register_callback_query_handler(callback_search_karaoke_command, Text(equals='search_karaoke'))

    dp.register_message_handler(search_karaoke, state=KaraokeSearch.name)

    dp.register_callback_query_handler(callback_subscribe_to_karaoke, Text(startswith='subscribe_to'))

    dp.register_message_handler(order_track_command, commands=['order_track'])

    dp.register_message_handler(
        add_link,
        Text(startswith=[
            'https://www.youtube.com/watch?v=',
            'https://youtu.be/',
            'https://xminus.me/track/'
        ]),
        state=OrderTrack.link
    )

    dp.register_message_handler(link_is_invalid, content_types='any', state=OrderTrack.link)

    # dp.register_message_handler(show_my_orders_command, commands=['show_my_orders'])
