from collections import deque
from aiogram.types import User
from typing import Type, List
from .types import Track, TrackStatus, TrackWaited, YouTubeTrack, XMinusTrack


class KaraokeUser:

    def __init__(self, aiogram_user: User):
        self.aiogram_user = aiogram_user
        self.playlist: List[Track] = []
        self.next_track_waited = self.get_next_track_with_status(TrackWaited)
        self.condition_issuing_tracks = True

    def get_next_track_with_status(self, status: Type[TrackStatus]):
        while True:
            for track in self.playlist:
                if isinstance(track.status, status):
                    yield track
            while self.condition_issuing_tracks:
                yield None

    def add_track_to_queue(self, track_url):
        if not isinstance(track_url, str):
            raise ValueError("Url should be an instance of <str>")
        track = self.get_track_instance(track_url)
        self.playlist.append(track)

    def pop_next_track(self):
        return self.playlist.popleft() if self.playlist else None

    def del_track_from_queue(self, index: int):
        del self.playlist[index]
        self.track_queue_index =- 1

    @staticmethod
    def get_track_instance(track_url):
        if 'youtube.com' in track_url or 'youtu.be' in track_url:
            return YouTubeTrack(track_url)

        if 'xminus.me' in track_url:
            return XMinusTrack(track_url)

    def __str__(self):
        return f"KaraokeUser(user={self.aiogram_user}, track_queue={list(self.playlist)})"

    def __repr__(self):
        return self.__str__()


class Karaoke:
    def __init__(self, name: str, owner_id: int):
        self.name = name
        self.owner_id = owner_id
        self.user_queue: List[KaraokeUser] = []
        self.track_num: int = 1
        self.next_round = self.get_next_round()

    def get_next_round(self):
        while True:
            round_queue = self.get_next_round_queue()

            if not round_queue:  # либо конец очереди, либо треков вообще нет
                # организовать удаление
                self.change_condition_issuing_tracks(False)
                round_queue = self.get_next_round_queue()  # проверяем ещё раз, если это был конец очереди
                self.change_condition_issuing_tracks(True)
            yield round_queue

    def get_next_round_queue(self):
        round_queue = []
        for user in self.user_queue:
            track = next(user.next_track_waited)
            if track is not None:
                round_queue.append((user, track))
            # try:
            #     round_queue.append((user, next(user.next_track_waited)))
            # except StopIteration:
            #     pass
        return round_queue

    def change_condition_issuing_tracks(self, condition: bool):
        for user in self.user_queue:
            user.condition_issuing_tracks = condition

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
