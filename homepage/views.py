"""Главная страница и общий ответ 404 на основе шаблонов."""
from django.shortcuts import render
from web_ui import data_view


@data_view
def index(request, data):
    return render(request, 'homepage/index.html', data)


def not_found(request, exception):
    return render(request, 'errors/message.html', {
        'title': 'Страница не найдена',
        'message': 'Такого адреса нет в маршрутах проекта.',
        'back_route': 'homepage:index',
    }, status=404)
