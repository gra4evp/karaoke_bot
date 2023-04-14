from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hlink
from karaoke_bot.karaoke_gram.karaoke import ready_to_play_karaoke_list
# from keyboards.admin_keyboards import inline_admin_keyboard as keyboard
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from karaoke_bot.karaoke_gram.types import TrackRemoved


async def show_queue_command(message: types.Message):
    for karaoke in ready_to_play_karaoke_list:
        if karaoke.owner_id == message.from_user.id:
            index = 0
            track_number = 0
            while True:
                no_more_tracks = 0
                for user in karaoke.user_queue:
                    try:
                        track = user.playlist[index]
                        track_number += 1
                        keyboard = InlineKeyboardMarkup()
                        keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
                        keyboard.insert(InlineKeyboardButton(
                            text="❌ Remove from queue",
                            callback_data=f'rm_from_queue {karaoke.name} {user.aiogram_user.id} {index}'))
                        await message.answer(f"{track_number}. {hlink('Track', track.url)}\n"
                                             f"Ordered by: @{user.aiogram_user.username}\n"
                                             f"Karaoke: {karaoke.name}",
                                             reply_markup=keyboard,
                                             parse_mode='HTML')
                    except IndexError:
                        no_more_tracks += 1
                if no_more_tracks == len(karaoke.user_queue):
                    break
                index += 1


async def show_circular_queue_command(message: types.Message):
    for karaoke in ready_to_play_karaoke_list:
        if karaoke.owner_id == message.from_user.id:
            for user, track in next(karaoke.next_round):
                track_number = 1
                index = track_number - 1
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
                keyboard.insert(InlineKeyboardButton(
                    text="❌ Remove from queue",
                    callback_data=f'rm_from_queue {karaoke.name} {user.aiogram_user.id} {index}')
                )
                await message.answer(f"{track_number}. {hlink('Track', track.url)}\n"
                                     f"Ordered by: @{user.aiogram_user.username}\n"
                                     f"Karaoke: {karaoke.name}",
                                     reply_markup=keyboard,
                                     parse_mode='HTML')


async def callback_remove_from_queue(callback: types.CallbackQuery):
    karaoke_name, user_id, index = callback.data.replace('rm_from_queue ', '').split(' ')

    for karaoke in ready_to_play_karaoke_list:
        if karaoke_name == karaoke.name:
            for user in karaoke.user_queue:
                if int(user_id) == user.aiogram_user.id:
                    try:
                        user.playlist[int(index)].status = TrackRemoved()
                        await callback.answer()
                        await callback.message.edit_text(callback.message.text + f"\nTrack status: ❌ Removed",
                                                         parse_mode='HTML')

                        keyboard = InlineKeyboardMarkup()
                        keyboard.add(InlineKeyboardButton(text="Restore 🔧", callback_data='set_to_perform'))
                        await callback.message.edit_reply_markup(keyboard)
                    except IndexError:
                        await callback.message.answer("Error")
                    break
            break
    print(ready_to_play_karaoke_list)


def register_handlers_admin(dispatcher: Dispatcher):
    dispatcher.register_message_handler(show_queue_command, commands=['show_queue'])
    dispatcher.register_message_handler(show_circular_queue_command, commands=['show_circular_queue'])
    dispatcher.register_callback_query_handler(callback_remove_from_queue, Text(startswith='rm_from_queue'))
