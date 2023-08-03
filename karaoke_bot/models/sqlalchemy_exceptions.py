class TelegramProfileNotFoundError(Exception):
    def __init__(self, telegram_id: int):
        message = f"Telegram profile with id={telegram_id} not found."
        super().__init__(message)


class KaraokeNotFoundError(Exception):
    def __init__(self, karaoke_name: str):
        message = f"Karaoke with name '{karaoke_name}' not found."
        super().__init__(message)
