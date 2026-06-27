from django.urls import path

from .views import burn_rate_view


urlpatterns = [
    path('planning/burn-rate/', burn_rate_view, name='burn_rate'),
    path('businesses/<int:business_id>/planning/burn-rate/', burn_rate_view, name='business_burn_rate'),
]
