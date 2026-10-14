"""Корневые маршруты спортивного проекта."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('competitions/', include('events.urls')),
    path('participants/', include('athletes.urls')),
    path('teams/', include('clubs.urls')),
    path('results/', include('scores.urls')),
]
handler404 = 'homepage.views.not_found'
