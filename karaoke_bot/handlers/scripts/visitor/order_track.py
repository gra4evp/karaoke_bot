from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.visitor_states import OrderTrack
from karaoke_bot.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.handlers.scripts.common.other import register_telegram_user
from karaoke_bot.karaoke_gram.karaoke import add_track_to_queue
from karaoke_bot.models.sqlalchemy_data_utils import get_selected_karaoke_data, add_performance_to_visitor
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, KaraokeNotFoundError, \
    EmptyFieldError, InvalidAccountStateError


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
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="Change karaoke", callback_data='change_selected_karaoke'))
        await bot.send_message(
            chat_id=user_id,
            text=f"Please send a link to the track on YouTube or XMinus\n\n<b>Selected karaoke:</b> {karaoke_name}",
            reply_markup=keyboard,
            parse_mode='HTML'
        )


async def callback_go_to_karaoke_search(callback: types.CallbackQuery, state: FSMContext):
    pass


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


async def link_is_invalid(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Change karaoke", callback_data='change_selected_karaoke'))

    async with state.proxy() as data:
        karaoke_name = data.get('karaoke_name')

    await message.reply(
        f"The <b>link</b> must be in the format:\n"
        f"✅ - https://youtu.be/\n"
        f"✅ - https://www.youtube.com/\n\n"
        f"Please try again"
        f"\n\n<b>Selected karaoke:</b> {karaoke_name}",
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(order_track_command, commands=['order_track'])
    dp.register_message_handler(order_track_command, Text(equals='Order a track'))

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
