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
from unique_links_parse import get_unique_links, load_links_by_user_id
from sqlalchemy_orm import VisitorPerformance, Recommendations, engine
from sqlalchemy.orm import sessionmaker

# подключение к бд
Session = sessionmaker(bind=engine)
session = Session()

API_TOKEN = "5761106314:AAHRTn5aJwpIiswWNoRpphpuZh38GD-gsP0"
# API_TOKEN = "6157408135:AAGNyYeInRXTrbGVdx_qXaiWHgDxTJP2b5w"  # мой тестовый бот
bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

user_ids = {}
queue_ids = []

admin_id = 1206756552  # владелец бара
# admin_id = 345705084  # kuks_51
# admin_id = 375571119  # gra4evp
# admin_id = 134566371  # gleb_kukuruz


class FSMOrderTrack(StatesGroup):
    track_url = State()


unique_links = get_unique_links('id_url_all.csv')
links_by_user_id = load_links_by_user_id('links_by_user_id.json')


async def start(message: types.Message, state: FSMContext):
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

    user_ids[user_id][0].append(message.text)

    performance = VisitorPerformance(user_id=user_id, url=message.text, created_at=message.date)
    session.add(performance)
    session.commit()

    await message.answer('Success! Sing better than the original, I believe in you 😇')
    await get_recommendation(message)


async def get_recommendation(message: types.Message):
    user_id = message.from_user.id

    links = links_by_user_id.get(str(user_id))
    if links:
        link = links.pop(random.randint(0, len(links) - 1))
        type_link = 'user_link'
    else:
        link = random.choice(list(unique_links))
        type_link = 'random_link'

    rec_message = await message.answer(f"{link}\n\nTest recommendation", parse_mode='HTML')

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Order this track", callback_data=f'order_this_track'))
    await rec_message.edit_reply_markup(keyboard)

    recommendation = Recommendations(user_id=user_id, message_id=rec_message.message_id, url=link, rec_type=type_link,
                                     is_accepted=False, created_at=message.date, updated_at=message.date)
    session.add(recommendation)
    session.commit()


async def state_order_track_is_invalid(message: types.Message):
    await message.answer('You added the link incorrectly, please try again 😉')


async def callback_order_this_track(callback: types.CallbackQuery):
    recommendation = session.query(Recommendations).filter(Recommendations.message_id == callback.message.message_id).first()

    recommendation.is_accepted = True
    recommendation.updated_at = callback.message.date

    performance = VisitorPerformance(user_id=callback.from_user.id,
                                     url=callback.message.text,
                                     created_at=callback.message.date)
    session.add(performance)

    if callback.from_user.id not in user_ids:
        user_ids[callback.from_user.id] = ([], callback.from_user.username)

    user_ids[callback.from_user.id][0].append(recommendation.url)

    await callback.answer('Success! Sing better than the original, I believe in you 😇')
    await callback.message.edit_text(f"✅ {hlink('Track', recommendation.url)} is ordered", parse_mode='HTML')
    session.commit()


async def join_a_group(message: types.Message):
    await message.answer('https://t.me/+JPb01AZkQgxkOGMy')


async def send_hello_text(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    if message.from_user.id != admin_id:
        keyboard.add(KeyboardButton("Order a track"))
        keyboard.add(KeyboardButton("Join a group of karaoke lovers"))
    else:
        keyboard.add(KeyboardButton("Get next link round"))
    await message.answer('Hello', reply_markup=keyboard)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start, commands=['start'], state='*')
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
    dispatcher.register_message_handler(state_order_track_is_invalid, content_types='any',
                                        state=FSMOrderTrack.track_url)

    dispatcher.register_callback_query_handler(callback_order_this_track, Text(startswith='order_this_track'))

    dispatcher.register_message_handler(send_hello_text, content_types='any')


if __name__ == "__main__":
    register_handlers(dispatcher)
    executor.start_polling(dispatcher, skip_updates=True)
