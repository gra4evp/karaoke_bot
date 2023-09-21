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


keyboard_back_to = InlineKeyboardMarkup()
keyboard_back_to.add(InlineKeyboardButton("<< Back to confirmation", callback_data='new_karaoke back confirmation'))
keyboard_back_to.insert(InlineKeyboardButton("<< Back to editing", callback_data='new_karaoke back editing'))


keyboard_create = InlineKeyboardMarkup()
keyboard_create.add(
    InlineKeyboardButton("✅ Create", callback_data='new_karaoke create force'),
    InlineKeyboardButton("<< Back", callback_data='new_karaoke back')
)


keyboard_cancel = InlineKeyboardMarkup()
keyboard_cancel.add(
    InlineKeyboardButton("❌ Cancel", callback_data='new_karaoke cancel force'),
    InlineKeyboardButton("<< Back", callback_data='new_karaoke back')
)

keyboards = {
    'confirm': keyboard_confirm,
    'edit': keyboard_edit,
    'back_to': keyboard_back_to,
    'create': keyboard_create,
    'cancel': keyboard_cancel
}
