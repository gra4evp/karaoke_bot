from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from karaoke_bot.create_bot import bot
import os
import qrcode


# def generate_qr_code(message: types.Message, bot_username: str, parameters: dict):
#
#     # bot_user: types.User = await bot.get_me()
#     delimeter = '-'
#     karaoke_name = 'Moya_prelest'
#     url = f'https://t.me/{bot_user.username}?start=func=search_karaoke{delimeter}karaoke_name={karaoke_name}'
#     qr = qrcode.make(url)
#
#     # Создаем папку, если ее нет
#     qr_codes_folder = os.path.join(os.getcwd(), 'qr_codes')
#     if not os.path.exists(qr_codes_folder):
#         os.makedirs(qr_codes_folder)
#
#     # Получение текущего рабочего каталога и создание пути к файлу
#     qr_path = os.path.join(qr_codes_folder, f'{message.from_user.id}_qr.png')
#     qr.save(qr_path)
#
#     # Отправка сохраненного изображения
#     with open(qr_path, 'rb') as photo:
#         await bot.send_photo(chat_id=message.from_user.id, photo=photo)
#
#     # Удаляем сохраненное изображение после отправки
#     os.remove(qr_path)
