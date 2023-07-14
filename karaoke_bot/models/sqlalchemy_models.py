from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, TIMESTAMP, func, DATETIME
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List

Base = declarative_base()


class TelegramProfile(Base):
    __tablename__ = 'telegram_profiles'

    account_id: Mapped[int] = mapped_column(Integer, ForeignKey('accounts.id'), unique=True, nullable=False)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_bot: Mapped[bool] = mapped_column(Boolean)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10))
    is_premium: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())

    account: Mapped["Account"] = relationship(back_populates='telegram_profile')


class Account(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())

    telegram_profile: Mapped["TelegramProfile"] = relationship(back_populates='account')
    ########################################### - дальше надо тестить
    #  One-to-many account-account_role
    account_role: Mapped[List["AccountRole"]] = relationship(back_populates='account')


class AccountRole(Base):
    __tablename__ = 'account_roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # пока не понятно имеет ли это смысл
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey('accounts.id'))
    role_id: Mapped[int] = mapped_column(Integer)
    role_type: Mapped[str] = mapped_column(String(20))

    account: Mapped["Account"] = relationship(back_populates='account_role')

    __mapper_args__ = {
        'polymorphic_identity': 'account_role',
        'polymorphic_on': role_type
    }


class Visitor(AccountRole):
    __tablename__ = 'visitors'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('account_roles.role_id'), primary_key=True)
    # selected_karaoke_id = Column(Integer)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    __mapper_args__ = {'polymorphic_identity': 'visitor'}


class Moderator(AccountRole):
    __tablename__ = 'moderators'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('account_roles.role_id'), primary_key=True)
    # karaoke_id = Column(Integer, ForeignKey('karaoke.id'))
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    __mapper_args__ = {'polymorphic_identity': 'moderator'}


class Owner(AccountRole):
    __tablename__ = 'owners'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('account_roles.role_id'), primary_key=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    __mapper_args__ = {'polymorphic_identity': 'owner'}


class Administrator(AccountRole):
    __tablename__ = 'administrators'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('account_roles.role_id'), primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    __mapper_args__ = {'polymorphic_identity': 'owner'}
#
#
# class VisitorPerformance(Base):
#     __tablename__ = 'visitor_performance'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     visitor_id = Column(Integer, ForeignKey('visitor.id'))
#     track_version_id = Column(Integer, ForeignKey('track_version.id'))
#     session_id = Column(Integer, ForeignKey('session.id'))
#
#
# class Session(Base):
#     __tablename__ = 'sessions'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     karaoke_id = Column(Integer, ForeignKey('karaoke.id'))
#     timestamp_from = Column(DateTime)
#     timestamp_to = Column(DateTime)
#
#
# class Karaoke(Base):
#     __tablename__ = 'karaoke'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name = Column(String(255))
#     active = Column(Boolean)
#     owner_id = Column(Integer, ForeignKey('owner.id'))
#     avatar_id = Column(Integer)
#     description = Column(String(255))
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#     moderators = relationship("ModeratorORM")
#
#
# class TrackVersion(Base):
#     __tablename__ = 'track_versions'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     track_id = Column(Integer, ForeignKey('track.id'))
#     url = Column(String(255))
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#
#
# class Track(Base):
#     __tablename__ = 'tracks'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name = Column(String(255))
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#
#
# class Artist(Base):
#     __tablename__ = 'artist'
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name = Column(String(255))


# engine = create_engine('mysql+pymysql://karaoke_bot:karaoke_bot@localhost/karaoke_db', echo=True)
engine = create_engine('sqlite:///karaoke_sqlaclhemy.db', echo=True)
Base.metadata.create_all(engine)

if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    with Session() as session:
        telegram_profile = TelegramProfile(
            id=777777777,
            is_bot=False,
            first_name='John',
            last_name='Doe',
            username='johndoe',
            language_code='en',
            is_premium=True
        )
        account = Account(telegram_profile=telegram_profile)
        session.add(account)
        session.commit()

    # with Session() as session:
    #     telegram_login = session.query(TelegramLogin).filter(TelegramLogin.id == 1).one()
    #     telegram_login.first_name = 'LEpexa'
    #     session.commit()

