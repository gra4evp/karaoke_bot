from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.visitor_states import KaraokeSearch
from karaoke_bot.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.handlers.scripts.common.register_telegram_user import register_telegram_user
from karaoke_bot.models.sqlalchemy_data_utils import subscribe_to_karaoke, get_karaoke_data_by_name
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, KaraokeNotFoundError, \
    EmptyFieldError, InvalidAccountStateError
from karaoke_bot.models.sqlalchemy_models_without_polymorph import AlchemySession, Karaoke
from karaoke_bot.handlers.utils import format_subscribers_count
from .order_track import order_track_command


async def search_karaoke_command(message: types.Message):
    await message.answer(f"Enter the <b>NAME</b> of the virtual karaoke where you plan to perform.", parse_mode='HTML')
    await KaraokeSearch.name.set()


async def callback_search_karaoke_command(callback: types.CallbackQuery):
    await callback.answer()
    await search_karaoke_command(callback.message)


async def search_karaoke(message: types.Message, state: FSMContext):

    karaoke_name = message.text
    try:
        karaoke_data = get_karaoke_data_by_name(karaoke_name=karaoke_name, user_id=message.from_user.id)
    except KaraokeNotFoundError as e:
        print(f"ERROR OCCURRED: {e.args}")
        await message.reply(
            "Oops, there is no such karaoke yet.\n\n"
            "Try to get the <b>NAME</b> from the administrator of the institution where you are.",
            parse_mode='HTML'
        )
    else:
        caption = f"<b>Karaoke</b>: {karaoke_name}\n" \
                  f"<b>Owner</b>: @{karaoke_data['owner']['username']}\n" \
                  f"<b>Subscribers</b>: {karaoke_data['subscribers']['amount']}\n\n"

        if karaoke_data['description'] is not None:
            caption += karaoke_data['description']

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="Subscribe", callback_data=f"subscribe_to {karaoke_name}"))

        if karaoke_data['subscribers']['is_subscribed']:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('Order a track', callback_data='order_track'))
            caption += "\n\n✅ You have already subscribed!"

        if karaoke_data['avatar_id'] is not None:
            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=karaoke_data['avatar_id'],
                caption=caption,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await message.answer(caption, reply_markup=keyboard, parse_mode='HTML')
        await state.finish()


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

        # TODO пофиксить баг, с тем что после поиска /search_karaoke мы попадаем сразу в /order_track (примемлимо если сразу нажато было /order_track)
        # current_state = await state.get_state()
        await order_track_command(callback.message, state, callback.from_user.id)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(search_karaoke_command, commands=['search_karaoke'])
    dp.register_message_handler(search_karaoke_command, Text(startswith='search karaoke', ignore_case=True))

    dp.register_callback_query_handler(callback_search_karaoke_command, Text(equals='search_karaoke'), state='*')

    dp.register_message_handler(search_karaoke, state=KaraokeSearch.name)

    dp.register_callback_query_handler(callback_subscribe_to_karaoke, Text(startswith='subscribe_to'))
