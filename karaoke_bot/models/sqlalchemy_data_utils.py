from .sqlalchemy_models_without_polymorph import TelegramProfile, Account, Session
from aiogram import types


def create_or_update_telegram_profile(user: types.User) -> None:
    with Session() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=user.id).first()
        if telegram_profile is not None:
            for field, value in user:
                if getattr(telegram_profile, field) != value:
                    setattr(telegram_profile, field, value)
        else:
            telegram_profile = TelegramProfile(
                id=user.id,
                is_bot=user.is_bot,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                language_code=user.language_code,
                is_premium=user.is_premium
            )
            session.add(Account(telegram_profile=telegram_profile))
        session.commit()
