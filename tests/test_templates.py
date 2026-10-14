"""Проверки контекста, шаблонных состояний и статических файлов ПР6."""
from pathlib import Path
from unittest.mock import patch

import pytest
from django.contrib.staticfiles import finders
from django.test import Client
from django.test.utils import setup_test_environment

from models import Competition, Participant, Result, Team

setup_test_environment()
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_data():
    team = Team(1, 'СпортТех')
    event = Competition(1, 'Осенний забег 2026', '2026-10-15', 18, 2)
    first = Participant(1, 'Иван Петров', 20, team)
    second = Participant(2, 'Анна Смирнова', 18, None)
    people = [first, second]
    first.register(event, people)
    second.register(event, people)
    return {
        'teams': [team], 'competitions': [event], 'participants': people,
        'results': [Result(1, first, event, 745.0),
                    Result(2, second, event, 726.0)],
    }


@pytest.mark.parametrize('url,template', [
    ('/', 'homepage/index.html'),
    ('/competitions/', 'events/competition_list.html'),
    ('/competitions/1/', 'events/competition_detail.html'),
    ('/participants/', 'athletes/participant_list.html'),
    ('/participants/1/', 'athletes/participant_detail.html'),
    ('/teams/', 'clubs/team_list.html'),
    ('/teams/1/', 'clubs/team_detail.html'),
    ('/results/', 'scores/result_list.html'),
    ('/results/1/', 'scores/result_detail.html'),
])
def test_templates_used(url, template, sample_data):
    with patch('web_ui.load_data', return_value=sample_data):
        response = Client().get(url)
    names = [t.name for t in response.templates]
    assert response.status_code == 200
    assert template in names
    assert 'base.html' in names
    assert 'includes/navigation.html' in names


@pytest.mark.parametrize('url,message', [
    ('/competitions/', 'Соревнований пока нет.'),
    ('/participants/', 'Участников пока нет.'),
    ('/teams/', 'Команд пока нет.'),
    ('/results/', 'Результатов пока нет.'),
])
def test_empty_lists(url, message):
    data = {'teams': [], 'competitions': [], 'participants': [], 'results': []}
    with patch('web_ui.load_data', return_value=data):
        response = Client().get(url)
    assert response.status_code == 200
    assert message in response.content.decode()


def test_context_and_filters(sample_data):
    with patch('web_ui.load_data', return_value=sample_data):
        response = Client().get('/competitions/1/')
    assert response.context['competition'] is sample_data['competitions'][0]
    assert response.context['free_places'] == 0
    text = response.content.decode()
    assert '15.10.2026' in text
    assert '726,0' in text
    assert 'Без команды' in text
    assert 'Свободных мест нет' in text


def test_open_status(sample_data):
    sample_data['participants'][1].competitions.clear()
    sample_data['results'] = sample_data['results'][:1]
    with patch('web_ui.load_data', return_value=sample_data):
        text = Client().get('/competitions/1/').content.decode()
    assert 'Есть свободные места' in text


def test_cancelled_registration(sample_data):
    person = sample_data['participants'][0]
    person.cancel(sample_data['competitions'][0], sample_data['results'])
    with patch('web_ui.load_data', return_value=sample_data):
        text = Client().get('/participants/1/').content.decode()
    assert 'Нет активных регистраций' in text
    assert 'Регистраций пока нет.' in text
    assert 'Результатов пока нет.' in text


@pytest.mark.parametrize('asset', [
    'css/style.css', 'js/main.js', 'img/logo.svg',
])
def test_static_assets(asset):
    path = finders.find(f'homepage/{asset}')
    assert path is not None
    assert Path(path).stat().st_size > 0
    text = Client().get('/').content.decode()
    assert f'/static/homepage/{asset}' in text


def test_includes_used(sample_data):
    with patch('web_ui.load_data', return_value=sample_data):
        response = Client().get('/competitions/')
    names = [t.name for t in response.templates]
    assert 'events/includes/competition_card.html' in names
    assert 'events/includes/competition_status.html' in names


def test_views_do_not_build_html():
    for app in ['homepage', 'events', 'athletes', 'clubs', 'scores']:
        text = (ROOT / app / 'views.py').read_text()
        assert 'page(' not in text
        assert 'format_html' not in text
        assert '<html' not in text
    assert 'def page(' not in (ROOT / 'web_ui.py').read_text()
