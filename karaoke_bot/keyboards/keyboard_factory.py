from karaoke_bot.localization.localization_manager import LocalizationManager
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class KeyboardFactory:
    def __init__(self, lm: LocalizationManager):
        self.lm = lm

    def get_inline_keyboard(self, keyboard_name: str, lg_code='en'):
        buttons_dict = self.lm.get_local_obj(obj_name=keyboard_name, keys=['buttons'])

        if buttons_dict is not None:
            keyboard = InlineKeyboardMarkup()
            for button_dict in buttons_dict:
                button_text = button_dict[lg_code]
                callback_data = button_dict['callback_data']
                if button_dict['attach_mode'] == 'add':
                    keyboard.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))
                else:
                    keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=callback_data))
            return keyboard

        raise KeyError(f"{keyboard_name} does not have keys=['buttons']")
