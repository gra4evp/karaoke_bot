from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_en = ReplyKeyboardMarkup(resize_keyboard=True)

order_track = KeyboardButton("Order a track")
menu = KeyboardButton("Menu")
cancel = KeyboardButton("Cancel")

keyboard_en.add(order_track)
keyboard_en.add(menu)
keyboard_en.insert(cancel)
