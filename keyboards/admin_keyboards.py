from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


inline_admin_keyboard = InlineKeyboardMarkup(row_width=2)
inline_admin_keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
