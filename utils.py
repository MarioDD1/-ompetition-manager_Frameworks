"""Общие проверки данных и ввод пользователя."""

from datetime import date
from typing import TypeVar

from models import Competition, Participant, Result, Team

T = TypeVar("T", Competition, Participant, Result, Team)


def next_id(records: list[T]) -> int:
    """Возвращает следующий свободный идентификатор."""
    return max((item.id for item in records), default=0) + 1


def find_by_id(records: list[T], record_id: int) -> T:
    """Находит запись или сообщает, что она отсутствует."""
    for item in records:
        if item.id == record_id:
            return item
    raise ValueError(f'Запись с ID {record_id} не найдена.')


def require_name(name: str) -> str:
    """Удаляет крайние пробелы и запрещает пустое название."""
    name = name.strip()
    if not name:
        raise ValueError('Название или имя не должно быть пустым.')
    return name


def validate_date(value: str) -> str:
    """Проверяет календарную дату в формате ГГГГ-ММ-ДД."""
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError('Укажите дату в формате ГГГГ-ММ-ДД.')
    return value


def read_int(prompt: str) -> int:
    """Читает целое число; ошибку обрабатывает основной цикл."""
    return int(input(prompt))


def read_float(prompt: str) -> float:
    """Читает число с точкой или запятой."""
    return float(input(prompt).replace(',', '.'))
