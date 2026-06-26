from django.urls import path

from .views import expense_detail_view, expenses_view


urlpatterns = [
    path('expenses/', expenses_view, name='expenses'),
    path('expenses/<int:pk>/', expense_detail_view, name='expense_detail'),
    path('businesses/<int:business_id>/expenses/', expenses_view, name='business_expenses'),
    path('businesses/<int:business_id>/expenses/<int:pk>/', expense_detail_view, name='business_expense_detail'),
]
