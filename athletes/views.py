"""Контекст списков спортсменов и их карточек."""
from django.shortcuts import render
from web_ui import data_view, find, missing


@data_view
def participant_list(request, data):
    return render(request, 'athletes/participant_list.html', {
        'participants': data['participants'],
    })


@data_view
def participant_detail(request, data, participant_id):
    person = find(data['participants'], participant_id)
    if person is None:
        return missing(request, 'Участник не найден', 'athletes:list')
    return render(request, 'athletes/participant_detail.html', {
        'participant': person,
        'results': [r for r in data['results'] if r.participant is person],
    })
