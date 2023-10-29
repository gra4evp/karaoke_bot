from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hlink
from karaoke_bot.karaoke_gram.karaoke import ready_to_play_karaoke_list
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from karaoke_bot.karaoke_gram.types import TrackRemoved
from karaoke_bot.karaoke_gram.utils import find_first_match_karaoke, find_first_match_track


async def show_queue_command(message: types.Message):
    karaoke = find_first_match_karaoke(ready_to_play_karaoke_list, where={'owner_id': message.from_user.id})
    if karaoke is not None:
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
                        callback_data=f'rm_from_queue {karaoke.name} {user.aiogram_user.id} {track.id}'))
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
    karaoke = find_first_match_karaoke(ready_to_play_karaoke_list, where={'owner_id': message.from_user.id})
    if karaoke is not None:
        for user, track in next(karaoke.next_round):
            track_number = 1
            index = track_number - 1
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
            keyboard.insert(InlineKeyboardButton(
                text="❌ Remove from queue",
                callback_data=f'rm_from_queue {karaoke.name} {user.aiogram_user.id} {track.id}')
            )
            await message.answer(f"{track_number}. {hlink('Track', track.url)}\n"
                                 f"Ordered by: @{user.aiogram_user.username}\n"
                                 f"Karaoke: {karaoke.name}",
                                 reply_markup=keyboard,
                                 parse_mode='HTML')


async def callback_remove_from_queue(callback: types.CallbackQuery):
    await callback.answer()
    karaoke_name, user_id, track_id = callback.data.replace('rm_from_queue ', '').split(' ')

    karaoke = find_first_match_karaoke(ready_to_play_karaoke_list, where={'owner_id': callback.from_user.id})
    if karaoke is not None:
        user = karaoke.find_first_match_user(where={'id': int(user_id)})
        if user is not None:
            track = user.find_first_match_track(where={'id': int(track_id)})
            track.remove()
            await callback.message.edit_text(callback.message.text + f"\nTrack status: ❌ Removed", parse_mode='HTML')
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text="Restore 🔧", callback_data='set_to_perform'))
            await callback.message.edit_reply_markup(keyboard)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(show_queue_command, commands=['show_queue'])
    dispatcher.register_message_handler(show_circular_queue_command, commands=['show_circular_queue'])
    dispatcher.register_callback_query_handler(callback_remove_from_queue, Text(startswith='rm_from_queue'))
