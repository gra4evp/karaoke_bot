from .sqlalchemy_models_without_polymorph import Karaoke, TelegramProfile, Account, AlchemySession, Owner
from aiogram import types


def create_or_update_telegram_profile(user: types.User) -> None:
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=user.id).first()
        if telegram_profile is not None:
            for field, value in user:
                if getattr(telegram_profile, field) != value:
                    setattr(telegram_profile, field, value)
                    print(f"ПОМЕНЯЛ {field} на {value}")
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


def karaoke_not_exists(karaoke_name: str) -> bool:
    """
    Checks if a karaoke with the given name exists in the database.

    Parameters:
        karaoke_name (str): The name of the karaoke to check for existence.

    Returns:
        bool: True, if a karaoke with the specified name does not exist in the database,
              False, if the karaoke already exists.
    """
    with AlchemySession() as session:
        karaoke = session.query(Karaoke).filter_by(name=karaoke_name).scalar()
    return karaoke is None


def create_karaoke(telegram_id: int, name: str, avatar_id: str, description: str) -> None:
    with AlchemySession() as session:

        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account

            owner = account.owner
            if owner is None:
                account.is_owner = True
                owner = Owner(account=account)
                session.add(owner)

            owner.karaokes.append(Karaoke(name=name, is_active=True, avatar_id=avatar_id, description=description))
        else:
            raise ValueError("TELEGRAM PROFILE SHOULD HAVE ALREADY EXISTED")
        session.commit()


def find_karaoke(karaoke_name: str) -> Karaoke | None:
    with AlchemySession() as session:
        karaoke = session.query(Karaoke).filter_by(name=karaoke_name).first()
    return karaoke
