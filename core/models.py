from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=128)
    type = models.CharField(
        max_length=50, choices=TYPE_CHOICES)
    description = models.CharField(
        max_length=255, blank=True)

    def __str__(self):
        return self.category_name

    class Meta:
        ordering = ['category_name']


class Income(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2)
    description = models.CharField(
        max_length=255, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"Income: £{self.amount} on {self.date}"

    class Meta:
        ordering = ['-date']


class Expense(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2)
    description = models.CharField(
        max_length=255, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"Expense: £{self.amount} on {self.date}"

    class Meta:
        ordering = ['-date']


class BudgetLimit(models.Model):
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE)
    limit_amount = models.DecimalField(
        max_digits=10, decimal_places=2)
    period = models.CharField(
        max_length=20, choices=PERIOD_CHOICES,
        default='monthly')
    warning_threshold = models.DecimalField(
        max_digits=5, decimal_places=2, default=80)
    start_date = models.DateField()

    def __str__(self):
        return f"{self.category} - £{self.limit_amount}"


class Bill(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    bill_name = models.CharField(max_length=128)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.bill_name

    class Meta:
        ordering = ['due_date']


class SavingsGoal(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=128)
    target_amount = models.DecimalField(
        max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.goal_name


#  Subscription Model
class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE)
    subscription_name = models.CharField(
        max_length=128)
    monthly_cost = models.DecimalField(
        max_digits=10, decimal_places=2)
    billing_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active')

    def __str__(self):
        return self.subscription_name

    class Meta:
        ordering = ['billing_date']