from collections import deque
from aiogram.types import User
from .types import Track, YouTubeTrack, XMinusTrack


class KaraokeUser:

    def __init__(self, user: User):
        self.aiogram_user = user
        self.track_queue: deque[Track] = deque()
        self.track_queue_index: int = 0

    def show_next_track(self):
        if not self.track_queue:  # track_queue is empty
            return None

        track = self.track_queue[self.track_queue_index]
        self.track_queue_index += 1

        if self.track_queue_index > len(self.track_queue) - 1:  # last_index
            self.track_queue_index = 0

        return track

    def add_track_to_queue(self, track_url):
        if not isinstance(track_url, str):
            raise ValueError("Url should be an instance of <str>")
        track = self.get_track_instance(track_url)
        self.track_queue.append(track)

    def pop_next_track(self):
        return self.track_queue.popleft() if self.track_queue else None

    def del_track_from_queue(self, index: int):
        del self.track_queue[index]
        self.track_queue_index =- 1

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
        self.user_queue_index: int = 0
        self.track_queue_index: int = 0
        self.track_num: int = 1

    def show_next_user(self):
        if not self.user_queue:  # user_queue is empty
            return None

        user = self.user_queue[self.user_queue_index]
        self.user_queue_index += 1

        if self.user_queue_index > len(self.user_queue) - 1:
            self.user_queue_index = 0
        return user

    # def get_next_round_queue(self) -> List:
    #     if not self.user_queue:
    #         return None
    #
    #     max_queue_index = max(user.track_queue_index for user in self.user_queue)
    #     if max_queue_index == 0:
    #         self.track_queue_index = 0
    #
    #     users_tracks = []
    #     for user in self.user_queue:
    #         if user.track_queue_index == max_queue_index:
    #             track = user.show_next_track()
    #             if track is not None:
    #                 self.track_queue_index += 1
    #                 users_tracks.append((self.track_queue_index, user, track))
    #     return users_tracks

    def get_next_round_queue(self):
        round = self.get_round_queue_by_index(self.track_queue_index)

        if round:
            self.track_queue_index += 1
        else:  # Или треков больше нет или мы попали в конец очереди
            round = self.get_round_queue_by_index(0)
            self.track_queue_index = 1 if round else 0

        return round

    def get_round_queue_by_index(self, index):
        round = []
        for user in self.user_queue:
            try:
                track = user.track_queue[index]
                round.append((self.track_num, user, track))
                self.track_num += 1
            except IndexError:
                self.track_num = 1
        return round

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
