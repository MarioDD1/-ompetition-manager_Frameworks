"""Проверки HTTP, связей, экранирования и сохранности JSON."""
import hashlib
import os
from unittest.mock import patch

import django
import pytest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportsite.settings')
django.setup()

from django.test import Client, override_settings  # noqa: E402
from django.urls import resolve, reverse  # noqa: E402
from storage import DATA_DIR, load_data  # noqa: E402


@pytest.fixture
def client():
    return Client()


@pytest.mark.parametrize('url,title', [
    ('/', 'Главная страница'),
    ('/competitions/', 'Соревнования'),
    ('/competitions/1/', 'Осенний забег 2026'),
    ('/participants/', 'Участники'),
    ('/participants/1/', 'Иван Петров'),
    ('/teams/', 'Команды'),
    ('/teams/1/', 'СпортТех'),
    ('/results/', 'Результаты'),
    ('/results/1/', 'Результат 1'),
])
def test_pages(client, url, title):
    response = client.get(url)
    assert response.status_code == 200
    assert 'text/html' in response['Content-Type']
    assert title in response.content.decode()
    assert '<html lang="ru">' in response.content.decode()
    for path in ('/', '/competitions/', '/participants/', '/teams/',
                 '/results/'):
        assert f'href="{path}"' in response.content.decode()


@pytest.mark.parametrize('url,title', [
    ('/competitions/999/', 'Соревнование не найдено'),
    ('/participants/999/', 'Участник не найден'),
    ('/teams/999/', 'Команда не найдена'),
    ('/results/999/', 'Результат не найден'),
])
def test_missing_objects(client, url, title):
    response = client.get(url)
    assert response.status_code == 404
    assert title in response.content.decode()


@pytest.mark.parametrize('url', ['/competitions/abc/', '/unknown/'])
@override_settings(DEBUG=False)
def test_invalid_routes(client, url):
    response = client.get(url)
    assert response.status_code == 404
    assert 'Страница не найдена' in response.content.decode()


def test_dynamic_url():
    path = reverse('events:detail', args=[1])
    assert path == '/competitions/1/'
    assert resolve(path).kwargs == {'competition_id': 1}


def test_links_and_ranking(client):
    text = client.get('/competitions/1/').content.decode()
    assert 'href="/participants/1/"' in text
    assert 'href="/results/1/"' in text
    assert 'href="/teams/1/"' in text
    scores = client.get('/results/').content.decode()
    assert scores.index('Анна Смирнова') < scores.index('Иван Петров')


def test_html_escaping(client):
    data = load_data()
    data['competitions'][0].name = '<script>alert(1)</script>'
    with patch('web_ui.load_data', return_value=data):
        text = client.get('/competitions/1/').content.decode()
    assert '<script>alert(1)</script>' not in text
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in text


def test_data_error(client):
    with patch('web_ui.load_data', side_effect=ValueError('bad json')):
        response = client.get('/')
    assert response.status_code == 503
    assert 'Данные временно недоступны' in response.content.decode()


def test_get_does_not_change_json(client):
    before = {p.name: hashlib.sha256(p.read_bytes()).digest()
              for p in DATA_DIR.glob('*.json')}
    for url in ('/', '/competitions/1/', '/participants/1/', '/results/'):
        assert client.get(url).status_code == 200
    after = {p.name: hashlib.sha256(p.read_bytes()).digest()
             for p in DATA_DIR.glob('*.json')}
    assert before == after


def test_read_only(client):
    response = client.post('/competitions/')
    assert response.status_code == 405
    assert response['Allow'] == 'GET, HEAD'


def test_head(client):
    response = client.head('/')
    assert response.status_code == 200
    assert response.content == b''
