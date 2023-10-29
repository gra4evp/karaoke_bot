from .karaoke import Karaoke
from typing import Any, List


def find_first_match_karaoke(karaokes: List[Karaoke], where: dict[str, Any]) -> Karaoke:
    # возвращает первое совпадение по условию
    for karaoke in karaokes:
        if all(getattr(karaoke, attr) == value for attr, value in where.items()):
            return karaoke
