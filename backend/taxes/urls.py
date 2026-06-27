from django.urls import path

from .views import tax_estimate_view, tax_rules_view


urlpatterns = [
    path('taxes/rules/', tax_rules_view, name='tax_rules'),
    path('taxes/estimate/', tax_estimate_view, name='tax_estimate'),
    path('businesses/<int:business_id>/taxes/rules/', tax_rules_view, name='business_tax_rules'),
    path('businesses/<int:business_id>/taxes/estimate/', tax_estimate_view, name='business_tax_estimate'),
]
