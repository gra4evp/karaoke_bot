from aiogram.dispatcher.filters.state import State, StatesGroup


class NewKaraoke(StatesGroup):
    name = State()
    # password = State()
    avatar = State()
    description = State()
    confirm = State()


class KaraokeSearch(StatesGroup):
    name = State()


class OrderTrack(StatesGroup):
    link = State()