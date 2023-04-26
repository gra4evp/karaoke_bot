from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import create_engine

Base = declarative_base()


class TelegramLogin(Base):
    __tablename__ = 'telegram_logins'

    account_id: Mapped[int] = mapped_column(Integer, ForeignKey('accounts.id'))
    id: Mapped[int] = mapped_column(primary_key=True)
    is_bot: Mapped[bool] = mapped_column(Boolean)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(32))
    language_code: Mapped[str] = mapped_column(String(10))
    is_premium: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime]

    account: Mapped["Account"] = relationship(back_populates='telegram_login')


class Account(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=DateTime(timezone=True))
    updated_at: Mapped[datetime]

    telegram_login: Mapped["TelegramLogin"] = relationship(back_populates='account')


# class VisitorORM(Base):
#     __tablename__ = 'visitors'
#
#     id = Column(Integer, primary_key=True)
#     selected_karaoke_id = Column(Integer)
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#
#
# class ModeratorORM(Base):
#     __tablename__ = 'moderators'
#
#     id = Column(Integer, primary_key=True)
#     karaoke_id = Column(Integer, ForeignKey('karaoke.id'))
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#
#
# class OwnerORM(Base):
#     __tablename__ = 'owners'
#
#     id = Column(Integer, primary_key=True)
#     password = Column(String(255))
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#
#
# class AdministratorORM(Base):
#     __tablename__ = 'administrators'
#
#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#
#
# class VisitorPerformanceORM(Base):
#     __tablename__ = 'visitor_performance'
#
#     id = Column(Integer, primary_key=True)
#     visitor_id = Column(Integer, ForeignKey('visitor.id'))
#     track_version_id = Column(Integer, ForeignKey('track_version.id'))
#     session_id = Column(Integer, ForeignKey('session.id'))
#
#
# class SessionORM(Base):
#     __tablename__ = 'sessions'
#
#     id = Column(Integer, primary_key=True)
#     karaoke_id = Column(Integer, ForeignKey('karaoke.id'))
#     timestamp_from = Column(DateTime)
#     timestamp_to = Column(DateTime)
#
#
# class KaraokeORM(Base):
#     __tablename__ = 'karaoke'
#
#     id = Column(Integer, primary_key=True)
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
# class TrackVersionORM(Base):
#     __tablename__ = 'track_versions'
#
#     id = Column(Integer, primary_key=True)
#     track_id = Column(Integer, ForeignKey('track.id'))
#     url = Column(String(255))
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#
#
# class TrackORM(Base):
#     __tablename__ = 'tracks'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(255))
#     created_at = Column(DateTime)
#     updated_at = Column(DateTime)
#
#
# class ArtistORM(Base):
#     __tablename__ = 'artist'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(255))



engine = create_engine('mysql+pymysql://user:password@localhost/mydatabase', echo=True)
Base.metadata.create_all(engine)
