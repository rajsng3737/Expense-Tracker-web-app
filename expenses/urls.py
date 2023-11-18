from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='expenses'),
    path('add-expense/', views.add_expense, name='add-expenses'),
    path('search-expenses/', views.search_expenses, name='search-expenses'),
    path('edit-expense/<int:id>/', views.expense_edit, name='expense-edit'),
    path('delete-expense/<int:id>/', views.delete_expense, name='delete-expense'),
    path('expense-category-summary/<str:period>/', views.expense_category_summary, name='expense-category-summary'),
    path('daywise-expenses/', views.daywise_expenses, name='daywise-expenses'),
    path('monthwise-report/', views.monthwise_report, name='monthwise-report'),
    path('monthly-report/', views.monthly_report, name='monthly-report'),
    path('settings/', views.settings, name='settings'),
]

