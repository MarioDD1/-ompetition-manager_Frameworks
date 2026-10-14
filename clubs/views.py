"""Контекст команд и их состава."""
from django.shortcuts import render
from web_ui import data_view, find, missing


@data_view
def team_list(request, data):
    rows = [
        {'team': team,
         'members_count': sum(p.team is team for p in data['participants'])}
        for team in data['teams']
    ]
    return render(request, 'clubs/team_list.html', {'teams': rows})


@data_view
def team_detail(request, data, team_id):
    team = find(data['teams'], team_id)
    if team is None:
        return missing(request, 'Команда не найдена', 'clubs:list')
    return render(request, 'clubs/team_detail.html', {
        'team': team,
        'members': [p for p in data['participants'] if p.team is team],
    })
