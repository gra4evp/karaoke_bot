from .karaoke import Karaoke, ready_to_play_karaoke_list
from typing import Any, List


def find_first_match_karaoke(
        where: dict[str, Any],
        karaokes: List[Karaoke] = ready_to_play_karaoke_list
) -> Karaoke:
    # возвращает первое совпадение по условию
    for kakaoke in karaokes:
        if all(getattr(kakaoke, attr) == value for attr, value in where.items()):
            return kakaoke
