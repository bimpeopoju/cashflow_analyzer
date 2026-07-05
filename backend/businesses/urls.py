from django.urls import path

from .views import businesses_view, business_tax_profile_view


urlpatterns = [
    path('businesses/', businesses_view, name='businesses'),
    path('tax-profile/', business_tax_profile_view, name='tax_profile'),
    path('businesses/<int:business_id>/tax-profile/', business_tax_profile_view, name='business_tax_profile'),
]
