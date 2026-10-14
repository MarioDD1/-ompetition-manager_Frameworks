"""Обработка коллекций результатов и статистика."""

from models import Competition, Participant, Result, Team
from utils import find_by_id, next_id


def add_result(
    results: list[Result], participants: list[Participant],
    competitions: list[Competition], participant_id: int,
    competition_id: int, time_seconds: float,
) -> Result:
    """Создаёт результат, связанный с объектами участника и соревнования."""
    person = find_by_id(participants, participant_id)
    event = find_by_id(competitions, competition_id)
    duplicate = any(r.participant is person and r.competition is event
                    for r in results)
    if duplicate:
        raise ValueError('Результат уже записан.')
    result = Result(next_id(results), person, event, time_seconds)
    results.append(result)
    return result


def sorted_results(results: list[Result], competition_id: int) -> list[Result]:
    """Сортирует результаты одного соревнования по времени."""
    selected = [r for r in results if r.competition.id == competition_id]
    return sorted(selected, key=lambda r: r.time_seconds)


def determine_place(
    result: float, first_result: float, second_result: float,
) -> int:
    """Сохранённая учебная функция ПР1 для трёх результатов."""
    if result <= first_result:
        return 1
    if result <= second_result:
        return 2
    return 3


def ranking(results: list[Result], competition_id: int) -> list[tuple]:
    """Возвращает пары (место, объект результата), учитывая равное время."""
    rows = []
    previous_time = None
    place = 0
    ordered = sorted_results(results, competition_id)
    for position, result in enumerate(ordered, 1):
        if result.time_seconds != previous_time:
            place = position
        rows.append((place, result))
        previous_time = result.time_seconds
    return rows


def statistics(
    participants: list[Participant], teams: list[Team], competition_id: int,
) -> dict:
    """Считает зарегистрированных участников и состав команд."""
    selected = [p for p in participants
                if any(c.id == competition_id for c in p.competitions)]
    by_team = {t.name: sum(p.team is t for p in selected) for t in teams}
    by_team['Без команды'] = sum(p.team is None for p in selected)
    return {'total': len(selected), 'by_team': by_team}
