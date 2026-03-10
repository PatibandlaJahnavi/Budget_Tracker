from django.shortcuts import (render, redirect,
                               get_object_or_404)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import (UserCreationForm,
                                        AuthenticationForm)
from django.contrib import messages
from django.db.models import Sum
import datetime
import json
from .models import (Income, Expense, Bill,
                     Category, BudgetLimit, SavingsGoal)
from .forms import (IncomeForm, ExpenseForm,
                    BudgetLimitForm, BillForm)
from .models import (Income, Expense, Bill,
                     Category, BudgetLimit,
                     SavingsGoal, Subscription) # ← add

# ═══════════════════════════════════════════════════════════
#   AUTHENTICATION VIEWS
# ═══════════════════════════════════════════════════════════

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                'Account created! Please login.')
            return redirect('login')
        else:
            messages.error(request,
                'Registration failed. Try again.')
    else:
        form = UserCreationForm()
    return render(request,
                  'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request,
                f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request,
                'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request,
                  'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request,
        'Logged out successfully.')
    return redirect('login')


# ═══════════════════════════════════════════════════════════
#   DASHBOARD VIEW
# ═══════════════════════════════════════════════════════════

@login_required
def dashboard(request):
    user = request.user
    today = datetime.date.today()

    # ── Totals ────────────────────────────────────────────
    total_income = Income.objects.filter(
        user=user
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_expense = Expense.objects.filter(
        user=user
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    balance = total_income - total_expense

    # ── Daily Allowance ───────────────────────────────────
    if today.month == 12:
        next_month = today.replace(
            year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(
            month=today.month + 1, day=1)

    days_left = (next_month - today).days
    daily_allowance = (float(balance) / days_left
                       if days_left > 0 else 0)

    # ── Recent Transactions ───────────────────────────────
    recent_expenses = Expense.objects.filter(
        user=user).order_by('-date')[:5]

    recent_incomes = Income.objects.filter(
        user=user).order_by('-date')[:5]

    # ── Upcoming Bills ────────────────────────────────────
    upcoming_bills = Bill.objects.filter(
        user=user,
        due_date__gte=today
    ).order_by('due_date')[:5]

    # ── Category Limits ───────────────────────────────────
    limits = BudgetLimit.objects.filter(user=user)
    for limit in limits:
        total_spent = Expense.objects.filter(
            user=user,
            category=limit.category
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        if limit.limit_amount > 0:
            limit.used_percent = round(
                (float(total_spent) /
                 float(limit.limit_amount)) * 100)
        else:
            limit.used_percent = 0

        limit.total_spent = total_spent

    # ── Chart Data ────────────────────────────────────────
    expenses_by_category = Expense.objects.filter(
        user=user,
        date__month=today.month,
        date__year=today.year
    ).values(
        'category__category_name'
    ).annotate(total=Sum('amount'))

    chart_labels = json.dumps([
        e['category__category_name'] or 'Uncategorized'
        for e in expenses_by_category
    ])
    chart_data = json.dumps([
        float(e['total'])
        for e in expenses_by_category
    ])

    return render(request, 'dashboard.html', {
        'balance': balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'daily_allowance': daily_allowance,
        'days_left': days_left,
        'recent_expenses': recent_expenses,
        'recent_incomes': recent_incomes,
        'upcoming_bills': upcoming_bills,
        'limits': limits,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'today': today,
    })


# ═══════════════════════════════════════════════════════════
#   INCOME VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request,
                'Income added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request,
                'Failed to add income.')
    else:
        form = IncomeForm()
    return render(request,
                  'add_transaction.html', {
        'form': form,
        'type': 'Income',
        'title': 'Add Income',
        'btn_color': 'btn-success',
    })


@login_required
def income_list(request):
    incomes = Income.objects.filter(
        user=request.user
    ).order_by('-date')

    total = incomes.aggregate(
        Sum('amount'))['amount__sum'] or 0

    return render(request, 'income_list.html', {
        'incomes': incomes,
        'total': total,
    })


@login_required
def delete_income(request, income_id):
    income = get_object_or_404(
        Income, id=income_id, user=request.user)
    income.delete()
    messages.success(request,
        'Income deleted successfully!')
    return redirect('income_list')


# ═══════════════════════════════════════════════════════════
#   EXPENSE VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request,
                'Expense added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request,
                'Failed to add expense.')
    else:
        form = ExpenseForm()
    return render(request,
                  'add_transaction.html', {
        'form': form,
        'type': 'Expense',
        'title': 'Add Expense',
        'btn_color': 'btn-danger',
    })


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(
        user=request.user
    ).order_by('-date')

    total = expenses.aggregate(
        Sum('amount'))['amount__sum'] or 0

    return render(request, 'expense_list.html', {
        'expenses': expenses,
        'total': total,
    })


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(
        Expense, id=expense_id, user=request.user)
    expense.delete()
    messages.success(request,
        'Expense deleted successfully!')
    return redirect('expense_list')


# ═══════════════════════════════════════════════════════════
#   CATEGORY VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def category_limits(request):
    if request.method == 'POST':
        form = BudgetLimitForm(request.POST)
        if form.is_valid():
            limit = form.save(commit=False)
            limit.user = request.user
            limit.save()
            messages.success(request,
                'Budget limit set successfully!')
            return redirect('category_limits')
        else:
            messages.error(request,
                'Failed to set limit.')
    else:
        form = BudgetLimitForm()

    categories = Category.objects.filter(
        user=request.user)
    limits = BudgetLimit.objects.filter(
        user=request.user)

    for limit in limits:
        total_spent = Expense.objects.filter(
            user=request.user,
            category=limit.category
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        if limit.limit_amount > 0:
            limit.used_percent = round(
                (float(total_spent) /
                 float(limit.limit_amount)) * 100)
        else:
            limit.used_percent = 0

        limit.total_spent = total_spent

        if limit.used_percent >= 100:
            limit.status = 'danger'
            limit.status_label = 'Over Budget'
        elif limit.used_percent >= 80:
            limit.status = 'warning'
            limit.status_label = 'Near Limit'
        else:
            limit.status = 'safe'
            limit.status_label = 'On Track'

    return render(request,
                  'category_limits.html', {
        'categories': categories,
        'limits': limits,
        'form': form,
    })


@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('category_name')
        type_ = request.POST.get('type')
        description = request.POST.get(
            'description', '')

        if name and type_:
            Category.objects.create(
                user=request.user,
                category_name=name,
                type=type_,
                description=description
            )
            messages.success(request,
                f'Category "{name}" added!')
        else:
            messages.error(request,
                'Please fill all fields.')

    return redirect('category_limits')


@login_required
def delete_category(request, category_id):
    category = get_object_or_404(
        Category, id=category_id,
        user=request.user)
    category.delete()
    messages.success(request,
        'Category deleted!')
    return redirect('category_limits')


@login_required
def delete_limit(request, limit_id):
    limit = get_object_or_404(
        BudgetLimit, id=limit_id,
        user=request.user)
    limit.delete()
    messages.success(request,
        'Budget limit removed!')
    return redirect('category_limits')


# ═══════════════════════════════════════════════════════════
#   BILL VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def bill_list(request):
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.user = request.user
            bill.save()
            messages.success(request,
                'Bill added successfully!')
            return redirect('bill_list')
        else:
            messages.error(request,
                'Failed to add bill.')
    else:
        form = BillForm()

    today = datetime.date.today()

    upcoming_bills = Bill.objects.filter(
        user=request.user,
        due_date__gte=today
    ).order_by('due_date')

    past_bills = Bill.objects.filter(
        user=request.user,
        due_date__lt=today
    ).order_by('-due_date')

    return render(request, 'bills.html', {
        'form': form,
        'upcoming_bills': upcoming_bills,
        'past_bills': past_bills,
        'today': today,
    })


@login_required
def delete_bill(request, bill_id):
    bill = get_object_or_404(
        Bill, id=bill_id, user=request.user)
    bill.delete()
    messages.success(request,
        'Bill deleted successfully!')
    return redirect('bill_list')


# ═══════════════════════════════════════════════════════════
#   SEARCH VIEW
# ═══════════════════════════════════════════════════════════

@login_required
def search_view(request):
    results = []
    categories = Category.objects.filter(
        user=request.user)

    date = request.GET.get('date', '')
    category_id = request.GET.get('category', '')
    type_filter = request.GET.get('type', '')
    amount_min = request.GET.get('amount_min', '')
    amount_max = request.GET.get('amount_max', '')

    if type_filter == 'income':
        queryset = Income.objects.filter(
            user=request.user)
    elif type_filter == 'expense':
        queryset = Expense.objects.filter(
            user=request.user)
    else:
        queryset = Expense.objects.filter(
            user=request.user)

    if date:
        queryset = queryset.filter(date=date)
    if category_id:
        queryset = queryset.filter(
            category_id=category_id)
    if amount_min:
        queryset = queryset.filter(
            amount__gte=amount_min)
    if amount_max:
        queryset = queryset.filter(
            amount__lte=amount_max)

    results = queryset.order_by('-date')

    return render(request, 'search.html', {
        'results': results,
        'categories': categories,
        'date': date,
        'category_id': category_id,
        'type_filter': type_filter,
        'amount_min': amount_min,
        'amount_max': amount_max,
    })


# ═══════════════════════════════════════════════════════════
#   SAVINGS GOALS VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def savings_goals(request):
    if request.method == 'POST':
        name = request.POST.get('goal_name')
        target = request.POST.get('target_amount')
        current = request.POST.get(
            'current_amount', 0)
        deadline = request.POST.get('deadline')

        if name and target and deadline:
            SavingsGoal.objects.create(
                user=request.user,
                goal_name=name,
                target_amount=target,
                current_amount=current or 0,
                deadline=deadline
            )
            messages.success(request,
                'Savings goal added!')
        else:
            messages.error(request,
                'Please fill all fields.')

    goals = SavingsGoal.objects.filter(
        user=request.user
    ).order_by('deadline')

    for goal in goals:
        if goal.target_amount > 0:
            goal.progress = round(
                (float(goal.current_amount) /
                 float(goal.target_amount)) * 100)
        else:
            goal.progress = 0

    return render(request,
                  'savings_goals.html', {
        'goals': goals,
    })


@login_required
def delete_goal(request, goal_id):
    goal = get_object_or_404(
        SavingsGoal, id=goal_id,
        user=request.user)
    goal.delete()
    messages.success(request,
        'Savings goal deleted!')
    return redirect('savings_goals')
# ═══════════════════════════════════════════════════════════
#   SUBSCRIPTION VIEWS
# ═══════════════════════════════════════════════════════════

@login_required
def subscription_list(request):
    if request.method == 'POST':
        name = request.POST.get('subscription_name')
        cost = request.POST.get('monthly_cost')
        billing = request.POST.get('billing_date')
        status = request.POST.get('status', 'active')

        if name and cost and billing:
            Subscription.objects.create(
                user=request.user,
                subscription_name=name,
                monthly_cost=cost,
                billing_date=billing,
                status=status
            )
            messages.success(request,
                'Subscription added successfully!')
        else:
            messages.error(request,
                'Please fill all fields.')

    subscriptions = Subscription.objects.filter(
        user=request.user
    ).order_by('billing_date')

    # total monthly cost
    total_monthly = subscriptions.filter(
        status='active'
    ).aggregate(
        Sum('monthly_cost')
    )['monthly_cost__sum'] or 0

    return render(request,
                  'subscription.html', {
        'subscriptions': subscriptions,
        'total_monthly': total_monthly,
    })


@login_required
def delete_subscription(request, sub_id):
    sub = get_object_or_404(
        Subscription, id=sub_id,
        user=request.user)
    sub.delete()
    messages.success(request,
        'Subscription deleted!')
    return redirect('subscription_list')