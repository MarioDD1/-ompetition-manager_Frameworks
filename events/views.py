"""Соревнования: подготовка контекста и вызов шаблонов."""
from django.shortcuts import render
from results import ranking
from web_ui import data_view, find, missing


@data_view
def competition_list(request, data):
    cards = [
        {'competition': event,
         'free_places': event.free_places(data['participants'])}
        for event in data['competitions']
    ]
    return render(request, 'events/competition_list.html', {'cards': cards})


@data_view
def competition_detail(request, data, competition_id):
    event = find(data['competitions'], competition_id)
    if event is None:
        return missing(request, 'Соревнование не найдено', 'events:list')
    context = {
        'competition': event,
        'free_places': event.free_places(data['participants']),
        'participants': [p for p in data['participants']
                         if event in p.competitions],
        'ranked_results': [
            {'place': place, 'result': result}
            for place, result in ranking(data['results'], event.id)
        ],
    }
    return render(request, 'events/competition_detail.html', context)
