from django.urls import path

from . import views

urlpatterns = [
    path('businesses/', views.businesses_view, name='businesses'),
    path('businesses/<int:business_id>/dashboard/', views.dashboard_view, name='business_dashboard'),
    path('businesses/<int:business_id>/sales/', views.sales_view, name='business_sales'),
    path('businesses/<int:business_id>/sales/<int:pk>/', views.sale_detail_view, name='business_sale_detail'),
    path('businesses/<int:business_id>/expenses/', views.expenses_view, name='business_expenses'),
    path('businesses/<int:business_id>/expenses/<int:pk>/', views.expense_detail_view, name='business_expense_detail'),
    path('businesses/<int:business_id>/inventory/', views.inventory_view, name='business_inventory'),
    path('businesses/<int:business_id>/inventory/<int:pk>/', views.inventory_detail_view, name='business_inventory_detail'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('sales/', views.sales_view, name='sales'),
    path('sales/<int:pk>/', views.sale_detail_view, name='sale_detail'),
    path('expenses/', views.expenses_view, name='expenses'),
    path('expenses/<int:pk>/', views.expense_detail_view, name='expense_detail'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('inventory/<int:pk>/', views.inventory_detail_view, name='inventory_detail'),
]
