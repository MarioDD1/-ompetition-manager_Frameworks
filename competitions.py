"""Функции обработки коллекции соревнований."""

from models import Competition, Participant
from utils import find_by_id, next_id


def add_competition(
    competitions: list[Competition], name: str, event_date: str,
    minimum_age: int, capacity: int,
) -> Competition:
    """Создаёт и добавляет объект соревнования."""
    event = Competition(next_id(competitions), name, event_date,
                        minimum_age, capacity)
    competitions.append(event)
    return event


def find_competitions(
    competitions: list[Competition], query: str,
) -> list[Competition]:
    """Ищет соревнования по части названия."""
    return [c for c in competitions if query.casefold() in c.name.casefold()]


def free_places(
    competitions: list[Competition], participants: list[Participant],
    competition_id: int,
) -> int:
    """Находит соревнование и делегирует ему подсчёт мест."""
    return find_by_id(competitions, competition_id).free_places(participants)
