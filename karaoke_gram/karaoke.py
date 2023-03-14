from typing import List, Dict
from collections import deque
from aiogram.types import User
from yt_dlp import YoutubeDL


class Track:

    def __init__(self, url):
        self.url = url
        self.info: Dict[str, str] = {}

    def get_info(self):
        raise NotImplementedError

    def __str__(self):
        pass

    def __repr__(self):
        pass


class YouTubeTrack(Track):

    def __init__(self, url: str):
        super().__init__(url)

    def get_info(self) -> Dict[str, str]:
        if not self.info:
            ydl_opts = {'quiet': True}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.info = {
                    'video_id': info.get('id', ''),
                    'title': info.get('title', ''),
                    'uploader': info.get('uploader', ''),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'comment_count': info.get('comment_count', 0),
                    'categories': info.get('categories', [])
                }
        return self.info

    def __str__(self) -> str:
        return f"YouTubeTrack: title - {self.info['title']} id - {self.info['video_id']}"

    def __repr__(self) -> str:
        return f"YouTubeTrack(url='{self.url}')"


class XMinusTrack(Track):
    def __init__(self, url: str):
        super().__init__(url)

    def get_info(self):
        if not self.info:
            # логика для получения информации о треке на xminus.com
            pass
        return self.info

    def __str__(self) -> str:
        return f"XMinusTrack: url - {self.url}"

    def __repr__(self) -> str:
        return f"XMinusTrack(url='{self.url}')"


class KaraokeUser:

    def __init__(self, user: User):
        self.aiogram_user = user
        self.track_queue: deque[Track] = deque()

    def add_track_to_queue(self, track_url):
        if not isinstance(track_url, str):
            raise ValueError("Url should be an instance of <str>")
        track = self.get_track_instance(track_url)
        self.track_queue.append(track)

    def pop_next_track(self):
        return self.track_queue.popleft() if self.track_queue else None

    @staticmethod
    def get_track_instance(track_url):
        if 'youtube.com' in track_url or 'youtu.be' in track_url:
            return YouTubeTrack(track_url)

        if 'xminus.me' in track_url:
            return XMinusTrack(track_url)

    def __str__(self):
        return f"KaraokeUser(user={self.aiogram_user}, track_queue={list(self.track_queue)})"

    def __repr__(self):
        return self.__str__()


class Karaoke:
    def __init__(self, name: str, owner_id: int):
        self.name = name
        self.owner_id = owner_id
        self.user_queue: deque[KaraokeUser] = deque()

    def add_user_to_queue(self, user: KaraokeUser):
        if not isinstance(user, KaraokeUser):
            raise ValueError("User should be an instance of KaraokeUser")
        self.user_queue.append(user)

    def pop_next_user(self) -> KaraokeUser:
        return self.user_queue.popleft() if self.user_queue else None

    def find_user(self, user_id: int) -> KaraokeUser:  # генератор возвращает первое совпадение по имени или None
        return next((user for user in self.user_queue if user.aiogram_user.id == user_id), None)

    def __str__(self):
        return f"Karaoke(name={self.name}, user_queue={list(self.user_queue)})"

    def __repr__(self):
        return self.__str__()


def find_first_match_karaoke(karaoke_name: str) -> Karaoke:
    # генератор возвращает первое совпадение по имени
    return next((karaoke for karaoke in ready_to_play_karaoke_list if karaoke.name == karaoke_name), None)


def add_track_to_queue(user: User, karaoke_name: str, owner_id: int, track_url: str) -> None:

    karaoke = find_first_match_karaoke(karaoke_name)
    if karaoke is None:  # Караоке ещё нет в списке
        karaoke = Karaoke(karaoke_name, owner_id)
        ready_to_play_karaoke_list.append(karaoke)

    karaoke_user = karaoke.find_user(user.id)
    if karaoke_user is None:  # Караоке есть, но такого пользователя в нем нет.
        karaoke_user = KaraokeUser(user)
        karaoke.add_user_to_queue(karaoke_user)

    karaoke_user.add_track_to_queue(track_url)
    print(ready_to_play_karaoke_list)


ready_to_play_karaoke_list: deque[Karaoke] = deque()
