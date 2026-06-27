from django.urls import path

from .views import forecast_view


urlpatterns = [
    path('forecasts/', forecast_view, name='forecast'),
    path('businesses/<int:business_id>/forecasts/', forecast_view, name='business_forecast'),
]
