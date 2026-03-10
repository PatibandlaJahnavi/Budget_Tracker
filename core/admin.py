from django.contrib import admin
from .models import (Category, Income, Expense,
                     BudgetLimit, Bill,
                     SavingsGoal, Subscription)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'type', 'user']
    list_filter = ['type']
    search_fields = ['category_name']


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount',
                    'category', 'date']
    list_filter = ['date', 'category']
    search_fields = ['description']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount',
                    'category', 'date']
    list_filter = ['date', 'category']
    search_fields = ['description']


@admin.register(BudgetLimit)
class BudgetLimitAdmin(admin.ModelAdmin):
    list_display = ['user', 'category',
                    'limit_amount', 'period']


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['user', 'bill_name',
                    'amount', 'due_date',
                    'is_recurring']
    list_filter = ['is_recurring', 'due_date']


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal_name',
                    'target_amount',
                    'current_amount', 'deadline']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription_name',
                    'monthly_cost',
                    'billing_date', 'status']
    list_filter = ['status']