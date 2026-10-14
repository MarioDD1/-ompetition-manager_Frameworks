"""Контекст результатов и мест в соревнованиях."""
from django.shortcuts import render
from results import ranking
from web_ui import data_view, find, missing


@data_view
def result_list(request, data):
    rows = []
    for event in data['competitions']:
        rows.extend({'place': place, 'result': result}
                    for place, result in ranking(data['results'], event.id))
    return render(request, 'scores/result_list.html', {'rows': rows})


@data_view
def result_detail(request, data, result_id):
    result = find(data['results'], result_id)
    if result is None:
        return missing(request, 'Результат не найден', 'scores:list')
    place = next(n for n, r in ranking(data['results'], result.competition.id)
                 if r is result)
    return render(request, 'scores/result_detail.html', {
        'result': result, 'place': place,
    })
