from django import forms
from .models import Income, Expense, BudgetLimit, Bill, Category


# ─── Income Form ─────────────────────────────────────────
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'category', 'date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter amount',
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter description',
                'class': 'form-control',
                'rows': 3
            }),
        }


# ─── Expense Form ─────────────────────────────────────────
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'date', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter amount',
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter description',
                'class': 'form-control',
                'rows': 3
            }),
        }


# ─── Budget Limit Form ────────────────────────────────────
class BudgetLimitForm(forms.ModelForm):
    class Meta:
        model = BudgetLimit
        fields = ['category', 'limit_amount', 'period', 'warning_threshold', 'start_date']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'limit_amount': forms.NumberInput(attrs={
                'placeholder': 'Enter limit amount',
                'class': 'form-control'
            }),
            'period': forms.Select(
                choices=[('monthly', 'Monthly'), ('weekly', 'Weekly')],
                attrs={'class': 'form-control'}
            ),
            'warning_threshold': forms.NumberInput(attrs={
                'placeholder': 'e.g. 80 for 80%',
                'class': 'form-control'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


# ─── Bill Form ────────────────────────────────────────────
class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['bill_name', 'amount', 'due_date', 'is_recurring']
        widgets = {
            'bill_name': forms.TextInput(attrs={
                'placeholder': 'Enter bill name',
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter amount',
                'class': 'form-control'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
