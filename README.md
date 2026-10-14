# Система управления спортивными соревнованиями
## Быстрый запуск Windows

Откройте CMD в распакованной папке с manage.py. Нужен Python 3.11
или другая совместимая с Django 5.2 версия Python.

```bat
py -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver
```

Откройте http://127.0.0.1:8000/. Остановка сервера — Ctrl+C.
В PowerShell окружение активируется командой `venv\Scripts\Activate.ps1`.
## Проверки и консоль

Команды выполняются именно из папки с manage.py:

```bat
python manage.py check
python -m pytest -v
python -m flake8 . --extend-exclude=venv
python manage.py findstatic homepage/css/style.css homepage/img/logo.svg homepage/js/main.js
python main.py
```

## Структура

| Путь | Назначение |
|---|---|
| sportsite/settings.py | Настройки проекта, язык ru-RU, время Europe/Moscow |
| sportsite/urls.py | Подключение маршрутов приложений |
| templates/base.html | Общий документ, title/content, static |
| templates/includes/navigation.html | Общая навигация через include |
| templates/errors/message.html | Шаблон ответов 404/405/503 |
| homepage/templates/homepage/index.html | Главная страница |
| events/templates/events/ | Список, карточка, включаемые компоненты соревнований |
| athletes/templates/athletes/ | Спортсмены и их регистрации |
| clubs/templates/clubs/ | Команды и состав |
| scores/templates/scores/ | Результаты и места |
| homepage/static/homepage/ | Собственные CSS, JavaScript, изображение |
| web_ui.py | Проверки метода запроса, загрузка JSON и ошибки без HTML |
| models.py, storage.py, data/ | Объектная модель и JSON из ПР3 |
| main.py, tests/ | Сохранённая консоль и автоматические проверки |

Уровень проекта подключён настройкой
`TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']`, APP_DIRS=True
ищет шаблоны внутри приложений. Имена шаблонов включают приложение,
поэтому файлы разных приложений не конфликтуют.

## Маршруты сохранены

| Адрес | View | Шаблон |
|---|---|---|
| / | homepage.views.index | homepage/index.html |
| /competitions/ | events.views.competition_list | events/competition_list.html |
| /competitions/1/ | events.views.competition_detail | events/competition_detail.html |
| /participants/ | athletes.views.participant_list | athletes/participant_list.html |
| /participants/1/ | athletes.views.participant_detail | athletes/participant_detail.html |
| /teams/ | clubs.views.team_list | clubs/team_list.html |
| /teams/1/ | clubs.views.team_detail | clubs/team_detail.html |
| /results/ | scores.views.result_list | scores/result_list.html |
| /results/1/ | scores.views.result_detail | scores/result_detail.html |

1 — пример существующего ID. В каждом приложении задан app_name,
списки названы list, карточки detail, главная index. Во всех ссылках
используется `{% url %}`, например `{% url 'events:detail' competition.id %}`.
Конвертеры `<int:...>` и старые адреса не изменены.

## Что изменилось

View загружает данные, подготавливает словарь context и вызывает render().
HTML-строки, page(), link(), card(), table() и format_html из веб-слоя
удалены. Основная цепочка запроса:

GET /competitions/1/ → sportsite/urls.py → events/urls.py →
competition_detail → load_data → context → events/competition_detail.html →
base.html и include-компоненты → HTTP 200.

Объекты передаются в контекст напрямую; вычисления, требующие аргументов,
остаются в Python. Например free_places вычисляется во view, а имя и дата
выводятся как competition.name и competition.date.

- extends и block: все самостоятельные страницы наследуют base.html,
  переопределяют title/content.
- include: navigation.html, competition_card.html, competition_status.html,
  ranking_table.html и team_link.html.
- for/empty: списки, регистрации, команды, результаты и отсутствие записей.
- if/else: наличие команды, активных регистраций и свободных мест.
- Фильтры: date форматирует дату, length считает элементы,
  default показывает «Без команды», floatformat:1 форматирует время.
- Автоэкранирование Django включено. Имена из JSON не выводятся через safe.
- static: style.css, main.js и logo.svg подключаются из base.html.
- main.js выводит текущий год в #current-year. CSS оформляет карточки,
  статусы и активный раздел, адаптирует интерфейс для узкого экрана.

Bootstrap подключён через CDN; собственный CSS позволяет пользоваться
страницами и без доступа к CDN. При DEBUG=True runserver обслуживает
статические файлы для учебного запуска.

## Состояния и ошибки

/competitions/999/, /participants/999/, /teams/999/, /results/999/:
возвращается шаблон с понятным сообщением и HTTP 404.
При неизвестном маршруте и DEBUG=False применяется общий шаблон ошибки;
при DEBUG=True Django показывает свою диагностическую страницу 404.
POST к странице просмотра возвращает 405, недоступные JSON — 503.

Пустые списки показывают сообщения. Соревнование без мест получает красный
статус; наличие свободных мест — зелёный. Спортсмен без команды отображается
как «Без команды». После отмены регистрации консолью на карточке спортсмена
исчезают эта регистрация и связанный результат. Если регистраций больше нет,
показывается «Нет активных регистраций». История отмен в JSON не хранится,
поэтому интерфейс не приписывает участнику выдуманный статус прошлого события.

## Данные и сохранность

JSON-файлы data/competitions.json, participants.json, teams.json, results.json
и исходные консольные модули сохранены без изменений. При каждом запросе
load_data() заново создаёт объекты и восстанавливает ссылки по ID.
Просмотр страниц не записывает данные. Консоль запускается `python main.py`.
SQLite создаётся migrate для встроенных таблиц Django, а предметные сущности
по-прежнему хранятся в JSON. База и venv в архив не включаются.