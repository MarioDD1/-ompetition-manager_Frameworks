"""Точка запуска системы спортивных соревнований."""

from copy import deepcopy
from datetime import date

from competitions import add_competition, find_competitions, free_places
from participants import (
    add_participant, add_team, cancel_registration,
    check_participant_access, find_participants, register_participant,
)
from results import add_result, determine_place, ranking, statistics
from storage import load_data, save_data
from utils import find_by_id, read_float, read_int

MENU = '''
1 — Соревнования
2 — Поиск соревнования
3 — Добавить соревнование
4 — Команды
5 — Добавить команду
6 — Участники
7 — Поиск участника
8 — Добавить участника
9 — Зарегистрировать на соревнование
10 — Отменить участие (с удалением результата)
11 — Записать результат в секундах
12 — Итоговая таблица
13 — Статистика соревнования
14 — Демонстрация сценария ПР1
0 — Выход
'''


def show_records(records: list) -> None:
    """Выводит записи коллекции."""
    if not records:
        print('Записей нет.')
    for item in records:
        print(item)


def demo_pr1() -> None:
    """Сохраняет первоначальный учебный сценарий без изменения данных."""
    print(f'Осенний забег 2026, дата: {date(2026, 10, 15)}')
    print('Участник: Иван Петров, команда: СпортТех, возраст: 20')
    if check_participant_access(20, 18):
        print('Участник допущен.')
        print('Учебное место среди трёх:', determine_place(12.45, 11.8, 12.1))
    else:
        print('Участник не допущен.')


def execute_action(choice: str, data: dict[str, list]) -> bool:
    """Выполняет пункт меню; возвращает признак изменения данных."""
    events = data['competitions']
    people = data['participants']
    teams = data['teams']
    scores = data['results']
    if choice == '1':
        for event in events:
            print(event, 'Свободных мест:',
                  free_places(events, people, event.id))
    elif choice == '2':
        show_records(find_competitions(events, input('Часть названия: ')))
    elif choice == '3':
        add_competition(events, input('Название: '),
                        input('Дата ГГГГ-ММ-ДД: '),
                        read_int('Минимальный возраст: '),
                        read_int('Количество мест: '))
    elif choice == '4':
        show_records(teams)
    elif choice == '5':
        add_team(teams, input('Название команды: '))
    elif choice == '6':
        show_records(people)
    elif choice == '7':
        show_records(find_participants(people, input('Часть имени: ')))
    elif choice == '8':
        name = input('Имя: ')
        age = read_int('Возраст: ')
        team_id = read_int('ID команды (0 — без команды): ')
        add_participant(people, teams, name, age,
                        None if team_id == 0 else team_id)
    elif choice == '9':
        print(register_participant(people, events,
                                   read_int('ID участника: '),
                                   read_int('ID соревнования: ')))
    elif choice == '10':
        cancel_registration(people, scores, read_int('ID участника: '),
                            read_int('ID соревнования: '))
    elif choice == '11':
        add_result(scores, people, events, read_int('ID участника: '),
                   read_int('ID соревнования: '), read_float('Время (с): '))
    elif choice == '12':
        event_id = read_int('ID соревнования: ')
        find_by_id(events, event_id)
        rows = ranking(scores, event_id)
        if not rows:
            print('Результатов пока нет.')
        for place, result in rows:
            print(f'{place}. {result}')
    elif choice == '13':
        event_id = read_int('ID соревнования: ')
        find_by_id(events, event_id)
        print(statistics(people, teams, event_id))
    elif choice == '14':
        demo_pr1()
    else:
        raise ValueError('Неизвестный пункт меню.')
    return choice in {'3', '5', '8', '9', '10', '11'}


def main() -> None:
    """Загружает данные и выполняет основной цикл меню."""
    try:
        data = load_data()
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f'Не удалось загрузить данные: {error}')
        print('Исправьте файлы в data. Исходные файлы не перезаписаны.')
        return
    print('=== Система управления спортивными соревнованиями ===')
    try:
        while True:
            print(MENU)
            choice = input('Выберите пункт: ').strip()
            if choice == '0':
                print('Работа завершена.')
                break
            candidate = deepcopy(data)
            try:
                changed = execute_action(choice, candidate)
                if changed:
                    save_data(candidate)
                    data = candidate
                    print('Изменения сохранены.')
            except (ValueError, OSError, KeyError, TypeError) as error:
                print(f'Ошибка: {error}')
    except (EOFError, KeyboardInterrupt):
        print('\nРабота завершена. Успешные изменения уже сохранены.')


if __name__ == '__main__':
    main()
