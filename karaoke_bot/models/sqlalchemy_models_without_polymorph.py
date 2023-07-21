from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, TIMESTAMP, func, DATETIME
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base, column_property
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List

Base = declarative_base()


class TelegramProfile(Base):
    __tablename__ = 'telegram_profiles'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), unique=True, nullable=False)
    id: Mapped[int] = mapped_column(primary_key=True)
    is_bot: Mapped[bool]
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10))
    is_premium: Mapped[bool] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())

    account: Mapped["Account"] = relationship(back_populates='telegram_profile')


class Account(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    is_visitor: Mapped[bool] = mapped_column(nullable=True)
    is_owner: Mapped[bool] = mapped_column(nullable=True)
    is_moderator: Mapped[bool] = mapped_column(nullable=True)
    is_administrator: Mapped[bool] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())

    telegram_profile: Mapped["TelegramProfile"] = relationship(back_populates='account')
    visitor: Mapped["Visitor"] = relationship(back_populates='account')
    owner: Mapped["Owner"] = relationship(back_populates='account')
    moderator: Mapped["Moderator"] = relationship(back_populates='account')
    administrator: Mapped["Administrator"] = relationship(back_populates='account')


class Visitor(Base):
    __tablename__ = 'visitors'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    selected_karaoke_id: Mapped[int] = mapped_column(ForeignKey('karaoke.id'), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())

    account: Mapped["Account"] = relationship(back_populates='visitor')
    karaoke: Mapped["Karaoke"] = relationship(back_populates='visitors')
    performances: Mapped[List["VisitorPerformance"]] = relationship(back_populates='visitor')


class Moderator(Base):
    __tablename__ = 'moderators'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    karaoke_id: Mapped[int] = mapped_column(ForeignKey('karaoke.id'))
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    account: Mapped["Account"] = relationship(back_populates='moderator')
    karaoke: Mapped["Karaoke"] = relationship(back_populates='moderators')


class Owner(Base):
    __tablename__ = 'owners'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    # password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    account: Mapped["Account"] = relationship(back_populates='owner')
    karaoke: Mapped["Karaoke"] = relationship(back_populates='owner')


class Administrator(Base):
    __tablename__ = 'administrators'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    account: Mapped["Account"] = relationship(back_populates='administrator')


class VisitorPerformance(Base):
    __tablename__ = 'visitor_performances'

    id: Mapped[int] = mapped_column(primary_key=True)
    visitor_id: Mapped[int] = mapped_column(ForeignKey('visitors.account_id'))
    track_version_id: Mapped[int] = mapped_column(ForeignKey('track_versions.id'))
    session_id: Mapped[int] = mapped_column(ForeignKey('sessions.id'))

    visitor: Mapped["Visitor"] = relationship(back_populates='performances')
    session: Mapped["Session"] = relationship(back_populates='performance')
    track_version: Mapped["TrackVersion"] = relationship(back_populates='performances')


class Session(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    karaoke_id: Mapped[int] = mapped_column(ForeignKey('karaoke.id'))
    timestamp_from: Mapped[DateTime] = mapped_column(DATETIME)
    timestamp_to: Mapped[DateTime] = mapped_column(DATETIME)

    performance: Mapped["VisitorPerformance"] = relationship(back_populates='session')
    karaoke: Mapped["Karaoke"] = relationship(back_populates='session')


class Karaoke(Base):
    __tablename__ = 'karaoke'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    active: Mapped[bool]
    owner_id: Mapped[int] = mapped_column(ForeignKey('owners.account_id'))
    avatar_id: Mapped[int]
    description: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    visitors: Mapped[List["Visitor"]] = relationship(back_populates='karaoke')
    moderators: Mapped[List["Moderator"]] = relationship(back_populates='karaoke')
    owner: Mapped["Owner"] = relationship(back_populates='karaoke')
    session: Mapped["Session"] = relationship(back_populates='karaoke')


class TrackVersion(Base):
    __tablename__ = 'track_versions'

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey('tracks.id'))
    url: Mapped[str] = mapped_column(String(2048), index=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    performances: Mapped[List["VisitorPerformance"]] = relationship(back_populates='track_version')
    track: Mapped["Track"] = relationship(back_populates='versions')


tracks_artists = Table(
    'tracks_artists',
    Base.metadata,
    Column('track_id', Integer, ForeignKey('tracks.id')),
    Column('artist_id', Integer, ForeignKey('artist.id'))
)


class Track(Base):
    __tablename__ = 'tracks'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    versions: Mapped[List["TrackVersion"]] = relationship(back_populates='track')
    artists: Mapped[List["Artist"]] = relationship(secondary=tracks_artists, back_populates="tracks")


class Artist(Base):
    __tablename__ = 'artist'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    tracks: Mapped[List["Track"]] = relationship(secondary=tracks_artists, back_populates="artists")


# engine = create_engine('mysql+pymysql://karaoke_bot:karaoke_bot@localhost/karaoke_db', echo=True)
engine = create_engine('sqlite:///karaoke_sqlaclhemy.db', echo=True)
Base.metadata.create_all(engine)
AlchemySession = sessionmaker(bind=engine)


def sqlalchemy_create_account(id, first_name, last_name, username):
    with AlchemySession() as session:
        telegram_profile = TelegramProfile(
            id=id,
            is_bot=False,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language_code='en',
            is_premium=True
        )
        account = Account(
            telegram_profile=telegram_profile
        )
        session.add(account)
        session.commit()


def sqlalchemy_add_role(telegram_id: int, role: str):
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account = telegram_profile.account
            match role:
                case 'visitor':
                    account.is_visitor = True
                    account.visitor = Visitor(selected_karaoke_id=1)
                case 'owner':
                    pass
                case 'administrator':
                    pass
                case 'moderator':
                    pass

            session.commit()
        else:
            print("Telegram profile not found.")


if __name__ == '__main__':
    sqlalchemy_create_account(id=1234, first_name='Petr', last_name='Grachev', username='gra4evp')
    # sqlalchemy_add_role(telegram_id=1234, role='visitor')