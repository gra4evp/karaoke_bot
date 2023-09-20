from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def show_my_orders_command(message: types.Message):
    pass
    # query = sqlite_db.sql_find_user_record(message.from_user.id)
    # if query is None:
    #     await message.answer("Хотите подключиться к караоке?")
    # else:
    #     active_karaoke, karaoke_list = query
    #     karaoke = find_first_match_karaoke(active_karaoke)
    #     if karaoke is None:
    #         await message.answer("🗒 You haven't ordered any tracks yet")
    #     else:
    #         user = karaoke.find_user(message.from_user.id)
    #         queue_length = len(user.playlist)
    #         if queue_length:
    #             for i in range(queue_length):
    #                 keyboard = InlineKeyboardMarkup()
    #                 keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
    #                 keyboard.insert(InlineKeyboardButton(text="❌ Remove", callback_data=f'rm_track'))
    #                 await message.answer(f"{i + 1}. {hlink('Track', user.playlist[i].url)}\n"
    #                                      f"Karaoke: {karaoke.name}",
    #                                      reply_markup=keyboard,
    #                                      parse_mode='HTML')
    #         else:
    #             await message.answer("🗒 You haven't ordered any tracks yet")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_my_orders_command, commands=['show_my_orders'])
