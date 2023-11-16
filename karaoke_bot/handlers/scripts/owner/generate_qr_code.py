from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from karaoke_bot.create_bot import bot
from karaoke_bot.states.owner_states import QRCode
import os
import qrcode


async def get_qr_code_command(message: types.Message, state: FSMContext):
    await message.answer('Введите текст для кодирования в QR код')
    await QRCode.text.set()


async def generate_qr_code(message: types.Message, state: FSMContext):
    await state.finish()

    bot_user: types.User = await bot.get_me()
    delimeter = '-'
    karaoke_name = 'Lada'
    url = f'https://t.me/{bot_user.username}?start=func=search_karaoke{delimeter}karaoke_name={karaoke_name}'
    qr = qrcode.make(url)

    # Создаем папку, если ее нет
    qr_codes_folder = os.path.join(os.getcwd(), 'qr_codes')
    if not os.path.exists(qr_codes_folder):
        os.makedirs(qr_codes_folder)

    # Получение текущего рабочего каталога и создание пути к файлу
    qr_path = os.path.join(qr_codes_folder, f'{message.from_user.id}_qr.png')
    qr.save(qr_path)

    # Отправка сохраненного изображения
    with open(qr_path, 'rb') as photo:
        await bot.send_photo(chat_id=message.from_user.id, photo=photo)

    # Удаляем сохраненное изображение после отправки
    os.remove(qr_path)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(get_qr_code_command, commands=['get_qr_code'], state='*')
    dp.register_message_handler(generate_qr_code, state=QRCode.text)