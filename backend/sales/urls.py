from django.urls import path

from .views import sale_detail_view, sales_view


urlpatterns = [
    path('sales/', sales_view, name='sales'),
    path('sales/<int:pk>/', sale_detail_view, name='sale_detail'),
]
