from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_confirm = InlineKeyboardMarkup()
keyboard_confirm.add(InlineKeyboardButton('✅ Confirm and Create', callback_data='new_karaoke create'))
keyboard_confirm.insert(InlineKeyboardButton('✏️ Edit', callback_data='new_karaoke edit'))
keyboard_confirm.add(InlineKeyboardButton('❌ Cancel', callback_data='new_karaoke cancel'))


keyboard_edit = InlineKeyboardMarkup()
keyboard_edit.add(InlineKeyboardButton("💬 Edit name", callback_data='new_karaoke edit name'))
keyboard_edit.insert(InlineKeyboardButton("🖼 Edit avatar", callback_data='new_karaoke edit avatar'))
keyboard_edit.add(InlineKeyboardButton("🗒 Edit description", callback_data='new_karaoke edit description'))
keyboard_edit.add(InlineKeyboardButton("<< Back", callback_data='new_karaoke back'))


keyboards = {
    'confirm': keyboard_confirm,
    'edit': keyboard_edit
}