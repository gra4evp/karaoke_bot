from aiogram.utils import executor
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,\
    InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
import random
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.markdown import hlink
from karaoke_bot.bot_old_version.unique_links_parse import load_links_by_user_id, get_unique_links

API_TOKEN = "5761106314:AAHRTn5aJwpIiswWNoRpphpuZh38GD-gsP0"
# API_TOKEN = "6157408135:AAGNyYeInRXTrbGVdx_qXaiWHgDxTJP2b5w"  # мой тестовый бот
bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

user_ids = {}
queue_ids = []

# admin_id = 1206756552  # владелец бара
# admin_id = 345705084  # kuks_51
# admin_id = 375571119  # gra4evp
admin_id = 134566371  # gleb_kukuruz


class FSMOrderTrack(StatesGroup):
    track_url = State()


unique_links = get_unique_links('id_url_all.csv')
links_by_user_id = load_links_by_user_id('links_by_user_id.json')


async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    if message.from_user.id != admin_id:
        keyboard.add(KeyboardButton("Order a track"))
        keyboard.add(KeyboardButton("Join a group of karaoke lovers"))
    else:
        keyboard.add(KeyboardButton("Get next link round"))

    bot_info = await bot.get_me()
    await message.answer(f"Welcome, {message.from_user.first_name}!\nI'm  - <b>{bot_info.first_name}</b>, "
                         f"the telegram bot of my favorite Venue bar. "
                         f"And I'm here to help you sing as many songs as possible! "
                         f"I hope you warmed up your vocal cords. 😏",
                         parse_mode='html',
                         reply_markup=keyboard)


async def get_next_link_round_command(message: types.Message):
    counter_empty = 0
    for user_id, value in user_ids.items():
        list_links, username = value
        if len(list_links):
            await message.answer(f"{hlink('Track', list_links.pop(0))} ordered by @{username}", parse_mode='HTML')
        else:
            counter_empty += 1

    if counter_empty == len(user_ids):
        await message.answer('Oops, Seems the songs are over.')


async def order_track_command(message: types.Message):
    await message.answer('Good! Add youtube link 😉')
    await FSMOrderTrack.track_url.set()


async def add_link(message: types.Message, state: FSMContext):
    await state.finish()

    user_id = message.from_user.id

    if user_id not in user_ids:
        user_ids[user_id] = ([], message.from_user.username)

    text = message.text
    time = message.date

    user_ids[user_id][0].append(text)
    print(f'{user_id}, {text}, {time}')
    await message.answer('Success! Sing better than the original, I believe in you 😇')

    # ---------------------------------------------------------------------------------------------------------
    links = links_by_user_id.get(str(user_id))
    if links:
        link = links.pop(random.randint(0, len(links) - 1))
        callback_data = 'order_this_track user_link'
    else:
        link = random.choice(list(unique_links))
        callback_data = 'order_this_track random_link'

    type_link = callback_data.replace('order_this_track ', '')
    print(f'rec: {user_id}, {link}, {time}, type_link: {type_link}')

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Order this track", callback_data=callback_data))

    # TODO попробовать сохранять объект message и использовать его
    await message.answer(f"{link}\n\nTest recomendation", reply_markup=keyboard, parse_mode='HTML')


async def state_order_track_is_invalid(message: types.Message):
    await message.answer('You added the link incorrectly, please try again 😉')


async def callback_order_this_track(callback: types.CallbackQuery):
    type_link = callback.data.replace('order_this_track ', '')

    user_id = callback.from_user.id
    text = callback.message.text.split('\n\n')

    link = text[0]
    user_ids[user_id][0].append(link)
    time = callback.message.date

    print(f'rec: {user_id}, {link}, {time}, accepted, type_link: {type_link}')
    await callback.answer('Success! Sing better than the original, I believe in you 😇')
    await callback.message.edit_text(f"✅ {hlink('Track', link)} is ordered", parse_mode='HTML')


async def join_a_group(message: types.Message):
    await message.answer('https://t.me/+JPb01AZkQgxkOGMy')


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start, commands=['start'])
    dispatcher.register_message_handler(join_a_group, Text(equals='Join a group of karaoke lovers', ignore_case=True))

    dispatcher.register_message_handler(order_track_command, commands=['order_track'])
    dispatcher.register_message_handler(order_track_command, Text('Order a track', ignore_case=True))

    dispatcher.register_message_handler(get_next_link_round_command, lambda message: message.from_user.id == admin_id,
                                        commands=['get_next_link_round'])
    dispatcher.register_message_handler(get_next_link_round_command, lambda message: message.from_user.id == admin_id,
                                        Text('Get next link round'))

    dispatcher.register_message_handler(add_link,
                                        Text(startswith=['https://www.youtube.com/watch?v=',
                                                         'https://youtu.be/',
                                                         'https://xminus.me/track/']),
                                        state=FSMOrderTrack.track_url)
    dispatcher.register_message_handler(state_order_track_is_invalid, content_types='Any',
                                        state=FSMOrderTrack.track_url)

    dispatcher.register_callback_query_handler(callback_order_this_track, Text(startswith='order_this_track'))


if __name__ == "__main__":
    register_handlers(dispatcher)
    executor.start_polling(dispatcher, skip_updates=True)
