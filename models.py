"""Объектная модель спортивных соревнований."""

from datetime import date
from math import isfinite


class Team:
    """Команда спортсменов."""

    def __init__(self, team_id: int, name: str) -> None:
        self.id = team_id
        self.name = self._name(name)

    @staticmethod
    def _name(value: str) -> str:
        """Проверяет название без обращения к состоянию объекта."""
        value = value.strip()
        if not value:
            raise ValueError('Название команды не должно быть пустым.')
        return value

    def __str__(self) -> str:
        return f'{self.id}: {self.name}'


class Competition:
    """Соревнование с возрастным ограничением и лимитом мест."""

    def __init__(
        self, competition_id: int, name: str, event_date: str,
        minimum_age: int, capacity: int,
    ) -> None:
        self.id = competition_id
        self.name = name.strip()
        self.date = date.fromisoformat(event_date)
        if not self.name or minimum_age < 0 or capacity <= 0:
            raise ValueError('Неверные название, возраст или число мест.')
        self.minimum_age = minimum_age
        self.capacity = capacity

    def allows_age(self, age: int) -> bool:
        """Проверяет возрастной допуск."""
        return age >= self.minimum_age

    def free_places(self, participants: list['Participant']) -> int:
        """Считает места по фактическим регистрациям."""
        occupied = sum(self in p.competitions for p in participants)
        return self.capacity - occupied

    def __str__(self) -> str:
        return (f'{self.id}: {self.name}, {self.date}, '
                f'от {self.minimum_age} лет, мест: {self.capacity}')


class Participant:
    """Участник с командой и ссылками на соревнования."""

    def __init__(
        self, participant_id: int, name: str, age: int,
        team: Team | None = None,
    ) -> None:
        self.id = participant_id
        self.name = name.strip()
        if not self.name or age < 0:
            raise ValueError('Неверные имя или возраст участника.')
        self.age = age
        self.team = team
        self.competitions: list[Competition] = []

    def register(
        self, competition: Competition, participants: list['Participant'],
    ) -> str:
        """Проверяет условия и изменяет регистрации этого спортсмена."""
        if competition in self.competitions:
            raise ValueError('Участник уже зарегистрирован.')
        if not competition.allows_age(self.age):
            raise ValueError('Участник не допущен по возрасту.')
        if competition.free_places(participants) <= 0:
            raise ValueError('Свободных мест нет.')
        self.competitions.append(competition)
        return f'Участник {self.name} зарегистрирован: {competition.name}.'

    def cancel(
        self, competition: Competition, results: list['Result'],
    ) -> None:
        """Отменяет регистрацию и удаляет связанный результат."""
        if competition not in self.competitions:
            raise ValueError('Регистрация на это соревнование отсутствует.')
        self.competitions.remove(competition)
        results[:] = [
            r for r in results
            if not (r.participant is self and r.competition is competition)
        ]

    def __str__(self) -> str:
        team = self.team.name if self.team else 'Без команды'
        events = ', '.join(str(c.id) for c in self.competitions) or 'нет'
        return (f'{self.id}: {self.name}, {self.age} лет, {team}, '
                f'соревнования: {events}')


class Result:
    """Время участника в конкретном соревновании."""

    def __init__(
        self, result_id: int, participant: Participant,
        competition: Competition, time_seconds: float,
    ) -> None:
        if competition not in participant.competitions:
            raise ValueError('Сначала зарегистрируйте участника.')
        if not isfinite(time_seconds) or time_seconds <= 0:
            raise ValueError('Время — конечное положительное число.')
        self.id = result_id
        self.participant = participant
        self.competition = competition
        self._time_seconds = time_seconds

    @property
    def time_seconds(self) -> float:
        """Предоставляет время для чтения без прямого изменения."""
        return self._time_seconds

    def __str__(self) -> str:
        return (f'{self.participant.name}: {self.time_seconds} с, '
                f'{self.competition.name}')
