from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

other_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

order_track = KeyboardButton("Order a track")
status = KeyboardButton("Status")
cancel = KeyboardButton("Cancel")

other_keyboard.add(order_track)
other_keyboard.add(status)
other_keyboard.insert(cancel)
