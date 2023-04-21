from dataclasses import dataclass
from datetime import datetime


@dataclass
class TelegramLogin:
    account_id: int
    id: int
    is_bot: bool
    first_name: str
    last_name: str
    username: str
    language_code: str
    is_premium: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Account:
    id: int
    created_at: datetime
    updated_at: datetime


@dataclass
class Visitor:
    id: int
    selected_karaoke_id: int
    created_at: datetime
    updated_at: datetime


@dataclass
class Moderator:
    id: int
    karaoke_id: int
    created_at: datetime
    updated_at: datetime


@dataclass
class Owner:
    id: int
    password: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Administrator:
    id: int
    created_at: datetime
    updated_at: datetime


@dataclass
class VisitorPerformance:
    id: int
    visitor_id: datetime
    track_version_id: datetime
    session_id: int


@dataclass
class Session:
    id: int
    karaoke_id: int
    timestamp_from: datetime.now()
    timestamp_to: datetime.now()


@dataclass
class Karaoke:
    id: int
    name: str
    active: bool
    owner_id: int
    avatar_id: int
    description: str
    created_at: datetime
    updated_at: datetime


@dataclass
class TrackVersion:
    id: int
    track_id: int
    url: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Track:
    id: int
    name: int
    created_at: datetime
    updated_at: datetime


@dataclass
class Artist:
    id: int
    name: int