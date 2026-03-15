from django.urls import path
from . import views

urlpatterns = [
    # Auth URLs
    path('login/',
         views.login_view,
         name='login'),

    path('logout/',
         views.logout_view,
         name='logout'),

    path('register/',
         views.register_view,
         name='register'),


    #  Dashboard
    path('',
         views.dashboard, name='dashboard'),
    path('dashboard/',
         views.dashboard,
         name='dashboard'),

    # Income
    path('income/',
         views.income_list, name='income_list'),
    path('income/add/',
         views.add_income, name='add_income'),
    path('income/delete/<int:income_id>/',
         views.delete_income, name='delete_income'),

    #  Expense
    path('expense/',
         views.expense_list, name='expense_list'),
    path('expense/add/',
         views.add_expense, name='add_expense'),
    path('expense/delete/<int:expense_id>/',
         views.delete_expense, name='delete_expense'),

    #  Categories
    path('categories/',
         views.category_limits,
         name='category_limits'),
    path('categories/add/',
         views.add_category, name='add_category'),
    path('categories/delete/<int:category_id>/',
         views.delete_category,
         name='delete_category'),
    path('limits/delete/<int:limit_id>/',
         views.delete_limit, name='delete_limit'),

    # Bills
    path('bills/',
         views.bill_list, name='bill_list'),
    path('bills/delete/<int:bill_id>/',
         views.delete_bill, name='delete_bill'),

    #  Search
    path('search/',
         views.search_view, name='search'),

    #  Savings
    path('savings/',
         views.savings_goals, name='savings_goals'),
    path('savings/delete/<int:goal_id>/',
         views.delete_goal, name='delete_goal'),
    path('profile/',
         views.profile,
         name='profile'),
    path('profile/edit/',
         views.edit_profile,
         name='edit_profile'),

    #  Subscriptions
    path('subscriptions/',
         views.subscription_list,
         name='subscription_list'),
    path('subscriptions/delete/<int:sub_id>/',
         views.delete_subscription,
         name='delete_subscription'),
]