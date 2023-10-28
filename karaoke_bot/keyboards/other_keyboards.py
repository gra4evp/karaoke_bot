from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

other_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

order_track = KeyboardButton("Order a track")
menu = KeyboardButton("Menu")
cancel = KeyboardButton("Cancel")

other_keyboard.add(order_track)
other_keyboard.add(menu)
other_keyboard.insert(cancel)
