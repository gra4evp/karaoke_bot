from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

client_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

b1 = KeyboardButton("Status")
b2 = KeyboardButton("Cancel")

client_keyboard.add(b1)
client_keyboard.insert(b2)


# inline_client_keyboards = InlineKeyboardMarkup(row_width=2)
# inl_b1 = InlineKeyboardButton(text="Sing here", callback_data="aaaa")
# inline_client_keyboards.add(inl_b1)
