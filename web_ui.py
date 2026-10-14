"""Общие проверки запросов и загрузка данных без формирования HTML."""
from functools import wraps
import logging

from django.shortcuts import render

from storage import load_data

logger = logging.getLogger(__name__)


def missing(request, title, route):
    """Возвращает шаблон отсутствующего объекта с HTTP 404."""
    return render(request, 'errors/message.html', {
        'title': title, 'message': 'Объект с таким ID отсутствует.',
        'back_route': route,
    }, status=404)


def data_view(view):
    """Загружает актуальные объекты ПР3 для каждого GET-запроса."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method not in ('GET', 'HEAD'):
            response = render(request, 'errors/message.html', {
                'title': 'Метод не поддерживается',
                'message': 'Эта страница доступна только для просмотра.',
                'back_route': 'homepage:index',
            }, status=405)
            response['Allow'] = 'GET, HEAD'
            return response
        try:
            data = load_data()
        except (OSError, ValueError, KeyError, TypeError):
            logger.exception('Не удалось загрузить JSON проекта.')
            return render(request, 'errors/message.html', {
                'title': 'Данные временно недоступны',
                'message': 'Проверьте JSON-файлы и журнал сервера.',
                'back_route': 'homepage:index',
            }, status=503)
        return view(request, data, *args, **kwargs)
    return wrapper


def find(items, object_id):
    """Находит объект или возвращает None для ответа 404."""
    return next((item for item in items if item.id == object_id), None)
