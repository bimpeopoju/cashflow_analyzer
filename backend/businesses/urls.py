from django.urls import path

from .views import businesses_view


urlpatterns = [
    path('businesses/', businesses_view, name='businesses'),
]
