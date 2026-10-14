"""Чтение и безопасная запись JSON-файлов."""

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from models import Competition, Participant, Result, Team
from utils import find_by_id

DATA_DIR = Path(__file__).resolve().parent / 'data'
FIELDS = {
    'competitions': {'id', 'name', 'date', 'minimum_age', 'capacity'},
    'participants': {'id', 'name', 'age', 'team_id', 'competition_ids'},
    'teams': {'id', 'name'},
    'results': {'id', 'participant_id', 'competition_id', 'time_seconds'},
}


def load_records(directory: Path = DATA_DIR) -> dict[str, list[dict]]:
    """Загружает файлы; при повреждении останавливает загрузку без записи."""
    data = {}
    for name, fields in FIELDS.items():
        path = directory / f'{name}.json'
        try:
            with path.open(encoding='utf-8') as file:
                records = json.load(file)
        except FileNotFoundError:
            raise ValueError(f'Отсутствует файл данных: {path.name}.')
        if not isinstance(records, list):
            raise ValueError(f'{path.name}: ожидается список записей.')
        ids = set()
        for record in records:
            if not isinstance(record, dict) or not fields <= record.keys():
                raise ValueError(f'{path.name}: неверная структура записи.')
            record_id = record['id']
            if (type(record_id) is not int or record_id <= 0
                    or record_id in ids):
                raise ValueError(f'{path.name}: неверный или повторный ID.')
            ids.add(record_id)
        data[name] = records
    return data


def save_data(data: dict[str, list], directory: Path = DATA_DIR) -> None:
    """Заменяет каждый JSON через временный файл, не обрывая его запись."""
    data = to_records(data)
    directory.mkdir(parents=True, exist_ok=True)
    for name in FIELDS:
        temporary = None
        try:
            with NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=directory,
                suffix='.tmp', delete=False,
            ) as file:
                temporary = Path(file.name)
                json.dump(data[name], file, ensure_ascii=False,
                          indent=2, allow_nan=False)
                file.write('\n')
            os.replace(temporary, directory / f'{name}.json')
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()


def load_data(directory: Path = DATA_DIR) -> dict[str, list]:
    """Создаёт объекты и восстанавливает ссылки по ID из формата ПР2."""
    raw = load_records(directory)
    teams = [Team(r['id'], r['name']) for r in raw['teams']]
    events = [Competition(r['id'], r['name'], r['date'],
                          r['minimum_age'], r['capacity'])
              for r in raw['competitions']]
    people = []
    for record in raw['participants']:
        team = (find_by_id(teams, record['team_id'])
                if record['team_id'] is not None else None)
        person = Participant(record['id'], record['name'], record['age'], team)
        for event_id in record['competition_ids']:
            person.register(find_by_id(events, event_id), people + [person])
        people.append(person)
    scores = []
    for record in raw['results']:
        person = find_by_id(people, record['participant_id'])
        event = find_by_id(events, record['competition_id'])
        if any(r.participant is person and r.competition is event
               for r in scores):
            raise ValueError('Повторный результат в JSON.')
        scores.append(Result(record['id'], person, event,
                             record['time_seconds']))
    return {'teams': teams, 'competitions': events,
            'participants': people, 'results': scores}


def to_records(data: dict[str, list]) -> dict[str, list[dict]]:
    """Преобразует объекты в JSON-совместимые записи и ID связей."""
    return {
        'teams': [{'id': t.id, 'name': t.name} for t in data['teams']],
        'competitions': [
            {'id': c.id, 'name': c.name, 'date': c.date.isoformat(),
             'minimum_age': c.minimum_age, 'capacity': c.capacity}
            for c in data['competitions']
        ],
        'participants': [
            {'id': p.id, 'name': p.name, 'age': p.age,
             'team_id': p.team.id if p.team else None,
             'competition_ids': [c.id for c in p.competitions]}
            for p in data['participants']
        ],
        'results': [
            {'id': r.id, 'participant_id': r.participant.id,
             'competition_id': r.competition.id,
             'time_seconds': r.time_seconds}
            for r in data['results']
        ],
    }
