from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('sales/', views.sales_view, name='sales'),
    path('sales/<int:pk>/', views.sale_detail_view, name='sale_detail'),
    path('expenses/', views.expenses_view, name='expenses'),
    path('expenses/<int:pk>/', views.expense_detail_view, name='expense_detail'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('inventory/<int:pk>/', views.inventory_detail_view, name='inventory_detail'),
]
