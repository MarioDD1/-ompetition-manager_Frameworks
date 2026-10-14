from django.urls import path
from . import views

app_name = 'scores'
urlpatterns = [
    path('', views.result_list, name='list'),
    path('<int:result_id>/', views.result_detail, name='detail'),
]
