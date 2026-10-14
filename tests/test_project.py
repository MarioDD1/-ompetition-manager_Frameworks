"""Проверки основных сценариев ПР2 на независимых данных."""

import json

import pytest

from competitions import add_competition, free_places
from participants import (
    add_participant, cancel_registration, find_participants,
    register_participant,
)
from results import add_result, ranking
from storage import load_data, save_data, to_records
from models import Competition, Participant, Result, Team


@pytest.fixture
def sample() -> dict:
    """Создаёт свежие данные для каждого теста."""
    data = {'competitions': [], 'participants': [], 'teams': [], 'results': []}
    add_competition(data['competitions'], 'Забег', '2026-10-15', 18, 2)
    add_participant(data['participants'], [], 'Иван Петров', 18, None)
    add_participant(data['participants'], [], 'Анна Смирнова', 20, None)
    add_participant(data['participants'], [], 'Олег Сидоров', 16, None)
    return data


def test_find_participant(sample: dict) -> None:
    """Поиск работает по части имени без учёта регистра."""
    found = find_participants(sample['participants'], 'ПЕТРОВ')
    assert [item.id for item in found] == [1]


def test_minimum_age_and_underage(sample: dict) -> None:
    """Граничный возраст допускается, меньший возраст отклоняется."""
    register_participant(sample['participants'], sample['competitions'], 1, 1)
    assert sample['participants'][0].competitions == sample['competitions']
    with pytest.raises(ValueError, match='возрасту'):
        register_participant(sample['participants'],
                             sample['competitions'], 3, 1)
    assert sample['participants'][2].competitions == []


def test_duplicate_registration(sample: dict) -> None:
    """Повторная регистрация запрещена и не занимает лишнее место."""
    register_participant(sample['participants'], sample['competitions'], 1, 1)
    with pytest.raises(ValueError, match='уже зарегистрирован'):
        register_participant(sample['participants'],
                             sample['competitions'], 1, 1)
    assert free_places(sample['competitions'], sample['participants'], 1) == 1


def test_cancel_registration(sample: dict) -> None:
    """Отмена освобождает место и удаляет результат участника."""
    register_participant(sample['participants'], sample['competitions'], 1, 1)
    add_result(sample['results'], sample['participants'],
               sample['competitions'], 1, 1, 100.0)
    cancel_registration(sample['participants'], sample['results'], 1, 1)
    assert sample['participants'][0].competitions == []
    assert sample['results'] == []


def test_ranking() -> None:
    """Места учитывают порядок времени и равные результаты."""
    event = Competition(1, 'Забег', '2026-10-15', 18, 5)
    people = [Participant(i, f'Участник {i}', 20) for i in range(1, 4)]
    for person in people:
        person.register(event, people)
    scores = [Result(i, person, event, time)
              for i, person, time in zip([1, 2, 3], people, [130, 100, 100])]
    rows = ranking(scores, 1)
    assert [result.id for place, result in rows] == [2, 3, 1]
    assert [place for place, result in rows] == [1, 1, 3]


def test_json_round_trip(sample: dict, tmp_path) -> None:
    """Данные сохраняются и точно восстанавливаются из JSON."""
    save_data(sample, tmp_path)
    restored = load_data(tmp_path)
    assert to_records(restored) == to_records(sample)


def test_corrupted_json_not_overwritten(sample: dict, tmp_path) -> None:
    """Повреждённый файл не заменяется пустыми данными при загрузке."""
    save_data(sample, tmp_path)
    path = tmp_path / 'competitions.json'
    path.write_text('broken json', encoding='utf-8')
    with pytest.raises(json.JSONDecodeError):
        load_data(tmp_path)
    assert path.read_text(encoding='utf-8') == 'broken json'


def test_invalid_result(sample: dict) -> None:
    """Нечисловые специальные значения и отрицательное время запрещены."""
    register_participant(sample['participants'], sample['competitions'], 1, 1)
    for value in [-1.0, 0.0, float('nan'), float('inf')]:
        with pytest.raises(ValueError, match='положительное'):
            add_result(sample['results'], sample['participants'],
                       sample['competitions'], 1, 1, value)
    assert sample['results'] == []


def test_str_and_constructor() -> None:
    """Конструкторы и строковое представление работают для всех сущностей."""
    team = Team(1, 'СпортТех')
    event = Competition(1, 'Забег', '2026-10-15', 18, 3)
    person = Participant(1, 'Иван', 20, team)
    person.register(event, [person])
    result = Result(1, person, event, 100)
    assert person.team is team
    assert result.participant is person
    assert result.competition is event
    assert all(str(item) for item in [team, event, person, result])
    assert 'Иван' in str(result)


def test_restored_object_links(sample: dict, tmp_path) -> None:
    """После JSON восстановлены ссылки на те же экземпляры объектов."""
    register_participant(sample['participants'], sample['competitions'], 1, 1)
    add_result(sample['results'], sample['participants'],
               sample['competitions'], 1, 1, 100)
    save_data(sample, tmp_path)
    restored = load_data(tmp_path)
    result = restored['results'][0]
    assert result.participant is restored['participants'][0]
    assert result.competition is restored['competitions'][0]
    assert result.participant.competitions[0] is result.competition
