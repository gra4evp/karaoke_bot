from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

other_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

search_karaoke = KeyboardButton('Search karaoke 🔍')
order_track = KeyboardButton("Order a track")
menu = KeyboardButton("Menu")
cancel = KeyboardButton("Cancel")

other_keyboard.add(search_karaoke)
other_keyboard.add(order_track)
other_keyboard.add(menu)
other_keyboard.insert(cancel)
