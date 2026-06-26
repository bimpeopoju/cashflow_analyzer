from django.urls import path

from .views import inventory_detail_view, inventory_view


urlpatterns = [
    path('inventory/', inventory_view, name='inventory'),
    path('inventory/<int:pk>/', inventory_detail_view, name='inventory_detail'),
    path('businesses/<int:business_id>/inventory/', inventory_view, name='business_inventory'),
    path('businesses/<int:business_id>/inventory/<int:pk>/', inventory_detail_view, name='business_inventory_detail'),
]
