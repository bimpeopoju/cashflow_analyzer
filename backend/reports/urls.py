from django.urls import path

from .views import reports_view


urlpatterns = [
    path('dashboard/', reports_view, name='dashboard'),
    path('reports/', reports_view, name='reports'),
    path('businesses/<int:business_id>/dashboard/', reports_view, name='business_dashboard'),
    path('businesses/<int:business_id>/reports/', reports_view, name='business_reports'),
]
