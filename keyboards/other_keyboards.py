from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

other_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

b1 = KeyboardButton("Status")
b2 = KeyboardButton("Cancel")

other_keyboard.add(b1)
other_keyboard.insert(b2)
