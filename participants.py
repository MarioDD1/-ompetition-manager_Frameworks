"""Операции над коллекциями участников и команд."""

from models import Competition, Participant, Result, Team
from utils import find_by_id, next_id


def add_team(teams: list[Team], name: str) -> Team:
    """Создаёт команду с уникальным названием."""
    if any(t.name.casefold() == name.strip().casefold() for t in teams):
        raise ValueError('Команда с таким названием уже существует.')
    team = Team(next_id(teams), name)
    teams.append(team)
    return team


def add_participant(
    participants: list[Participant], teams: list[Team], name: str,
    age: int, team_id: int | None,
) -> Participant:
    """Создаёт участника и связывает его с существующим объектом команды."""
    team = find_by_id(teams, team_id) if team_id is not None else None
    person = Participant(next_id(participants), name, age, team)
    participants.append(person)
    return person


def find_participants(
    participants: list[Participant], query: str,
) -> list[Participant]:
    """Ищет участников по части имени."""
    return [p for p in participants if query.casefold() in p.name.casefold()]


def check_participant_access(age: int, min_age: int) -> bool:
    """Сохраняет учебную проверку ПР1."""
    return age >= min_age


def register_participant(
    participants: list[Participant], competitions: list[Competition],
    participant_id: int, competition_id: int,
) -> str:
    """Находит объекты и вызывает метод регистрации участника."""
    person = find_by_id(participants, participant_id)
    event = find_by_id(competitions, competition_id)
    return person.register(event, participants)


def cancel_registration(
    participants: list[Participant], results: list[Result],
    participant_id: int, competition_id: int,
) -> None:
    """Находит существующую регистрацию и вызывает метод отмены."""
    person = find_by_id(participants, participant_id)
    matches = (c for c in person.competitions if c.id == competition_id)
    event = next(matches, None)
    if event is None:
        raise ValueError('Участник не зарегистрирован на это соревнование.')
    person.cancel(event, results)
