from django.urls import path

from .views import capital_view


urlpatterns = [
    path('businesses/<int:business_id>/capital/', capital_view, name='capital'),
]
