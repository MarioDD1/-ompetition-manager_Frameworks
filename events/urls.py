from django.urls import path
from . import views

app_name = 'events'
urlpatterns = [
    path('', views.competition_list, name='list'),
    path('<int:competition_id>/', views.competition_detail, name='detail'),
]
