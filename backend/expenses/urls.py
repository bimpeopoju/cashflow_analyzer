from django.urls import path

from .views import expense_detail_view, expenses_view


urlpatterns = [
    path('expenses/', expenses_view, name='expenses'),
    path('expenses/<int:pk>/', expense_detail_view, name='expense_detail'),
]
