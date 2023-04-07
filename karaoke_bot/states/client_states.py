from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMNewKaraoke(StatesGroup):
    karaoke_name = State()
    karaoke_password = State()
    karaoke_avatar = State()


class FSMKaraokeSearch(StatesGroup):
    karaoke_name = State()


class FSMOrderTrack(StatesGroup):
    link = State()