from django.urls import path

from .views import break_even_view, burn_rate_view


urlpatterns = [
    path('planning/burn-rate/', burn_rate_view, name='burn_rate'),
    path('planning/break-even/', break_even_view, name='break_even'),
    path('businesses/<int:business_id>/planning/burn-rate/', burn_rate_view, name='business_burn_rate'),
    path('businesses/<int:business_id>/planning/break-even/', break_even_view, name='business_break_even'),
]
