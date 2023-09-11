from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.visitor_states import KaraokeSearch
from karaoke_bot.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.handlers.scripts.common.other import register_telegram_user
from karaoke_bot.models.sqlalchemy_data_utils import subscribe_to_karaoke
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

        # TODO пофиксить баг, с тем что после поиска /search_karaoke мы попадаем сразу в /order_track (примемлимо если сразу нажато было /order_track)
        # current_state = await state.get_state()
        await order_track_command(callback.message, state, callback.from_user.id)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(search_karaoke_command, commands=['search_karaoke'])

    dp.register_callback_query_handler(callback_search_karaoke_command, Text(equals='search_karaoke'), state='*')

    dp.register_message_handler(search_karaoke, state=KaraokeSearch.name)

    dp.register_callback_query_handler(callback_subscribe_to_karaoke, Text(startswith='subscribe_to'))