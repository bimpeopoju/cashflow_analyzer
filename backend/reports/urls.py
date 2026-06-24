from django.urls import path

from .views import reports_view


urlpatterns = [
    path('dashboard/', reports_view, name='dashboard'),
    path('reports/', reports_view, name='reports'),
]
