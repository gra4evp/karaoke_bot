from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.create_bot import bot
import os
import qrcode


async def callback_generate_qr_code(callback: types.CallbackQuery):

    bot_user: types.User = await bot.get_me()
    delimeter = '-'
    karaoke_name = callback.data.split(' ')[1]
    url = f'https://t.me/{bot_user.username}?start=func=search_karaoke{delimeter}karaoke_name={karaoke_name}'
    qr = qrcode.make(url)

    qr_codes_folder = os.path.join(os.getcwd(), 'qr_codes')  # Создаем папку, если ее нет
    if not os.path.exists(qr_codes_folder):
        os.makedirs(qr_codes_folder)

    qr_path = os.path.join(qr_codes_folder, f'{callback.from_user.id}_qr.png')
    qr.save(qr_path)

    with open(qr_path, 'rb') as photo:
        await bot.send_photo(chat_id=callback.from_user.id, photo=photo)

    os.remove(qr_path)  # Удаляем сохраненное изображение после отправки


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(callback_generate_qr_code, Text(startswith='get_qr_code'))
