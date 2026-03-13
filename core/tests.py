from django.test import TestCase

# Create your tests here.
from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .forms import IncomeForm, ExpenseForm, BudgetLimitForm, BillForm
from .models import (
    Category,
    Income,
    Expense,
    BudgetLimit,
    Bill,
    SavingsGoal,
    Subscription,
)

# MODEL TESTS
class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123'
        )

        self.expense_category = Category.objects.create(
            user=self.user,
            category_name='Food',
            type='expense',
            description='Food expenses'
        )

        self.income_category = Category.objects.create(
            user=self.user,
            category_name='Salary',
            type='income',
            description='Monthly salary'
        )

    def test_category_str(self):
        self.assertEqual(str(self.expense_category), 'Food')

    def test_income_str(self):
        income = Income.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1500.00'),
            description='Salary payment',
            date=date(2026, 3, 10)
        )
        self.assertEqual(
            str(income),
            'Income: £1500.00 on 2026-03-10'
        )

    def test_expense_str(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('25.50'),
            description='Lunch',
            date=date(2026, 3, 11)
        )
        self.assertEqual(
            str(expense),
            'Expense: £25.50 on 2026-03-11'
        )

    def test_budget_limit_str(self):
        limit = BudgetLimit.objects.create(
            user=self.user,
            category=self.expense_category,
            limit_amount=Decimal('500.00'),
            period='monthly',
            warning_threshold=Decimal('80.00'),
            start_date=date(2026, 3, 1)
        )
        self.assertEqual(str(limit), 'Food - £500.00')

    def test_bill_str(self):
        bill = Bill.objects.create(
            user=self.user,
            bill_name='Electricity',
            amount=Decimal('60.00'),
            due_date=date(2026, 3, 20),
            is_recurring=True
        )
        self.assertEqual(str(bill), 'Electricity')

    def test_savings_goal_str(self):
        goal = SavingsGoal.objects.create(
            user=self.user,
            goal_name='Laptop',
            target_amount=Decimal('1200.00'),
            current_amount=Decimal('300.00'),
            deadline=date(2026, 6, 1)
        )
        self.assertEqual(str(goal), 'Laptop')

    def test_subscription_str(self):
        sub = Subscription.objects.create(
            user=self.user,
            subscription_name='Netflix',
            monthly_cost=Decimal('9.99'),
            billing_date=date(2026, 3, 15),
            status='active'
        )
        self.assertEqual(str(sub), 'Netflix')

    def test_category_ordering_by_name(self):
        Category.objects.create(
            user=self.user,
            category_name='Transport',
            type='expense'
        )
        Category.objects.create(
            user=self.user,
            category_name='Bills',
            type='expense'
        )

        categories = list(Category.objects.all())
        names = [c.category_name for c in categories]
        self.assertEqual(names, sorted(names))

    def test_income_ordering_by_date_desc(self):
        old_income = Income.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=date(2026, 3, 1)
        )
        new_income = Income.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('2000.00'),
            date=date(2026, 3, 10)
        )

        incomes = list(Income.objects.all())
        self.assertEqual(incomes[0], new_income)
        self.assertEqual(incomes[1], old_income)

    def test_bill_ordering_by_due_date_asc(self):
        later_bill = Bill.objects.create(
            user=self.user,
            bill_name='Internet',
            amount=Decimal('30.00'),
            due_date=date(2026, 3, 25)
        )
        earlier_bill = Bill.objects.create(
            user=self.user,
            bill_name='Water',
            amount=Decimal('20.00'),
            due_date=date(2026, 3, 15)
        )

        bills = list(Bill.objects.all())
        self.assertEqual(bills[0], earlier_bill)
        self.assertEqual(bills[1], later_bill)

    def test_expense_ordering_by_date_desc(self):
        old_expense = Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('10.00'),
            date=date(2026, 3, 1)
        )
        new_expense = Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('20.00'),
            date=date(2026, 3, 10)
        )

        expenses = list(Expense.objects.all())
        self.assertEqual(expenses[0], new_expense)
        self.assertEqual(expenses[1], old_expense)

    def test_subscription_default_status_is_active(self):
        sub = Subscription.objects.create(
            user=self.user,
            subscription_name='Spotify',
            monthly_cost=Decimal('10.99'),
            billing_date=date(2026, 3, 15)
        )
        self.assertEqual(sub.status, 'active')

    def test_bill_default_is_recurring_is_false(self):
        bill = Bill.objects.create(
            user=self.user,
            bill_name='Gas',
            amount=Decimal('45.00'),
            due_date=date(2026, 3, 18)
        )
        self.assertFalse(bill.is_recurring)

    def test_subscription_ordering_by_billing_date_asc(self):
        later_sub = Subscription.objects.create(
            user=self.user,
            subscription_name='Disney+',
            monthly_cost=Decimal('7.99'),
            billing_date=date(2026, 3, 25),
            status='active'
        )
        earlier_sub = Subscription.objects.create(
            user=self.user,
            subscription_name='Netflix',
            monthly_cost=Decimal('9.99'),
            billing_date=date(2026, 3, 15),
            status='active'
        )

        subscriptions = list(Subscription.objects.all())
        self.assertEqual(subscriptions[0], earlier_sub)
        self.assertEqual(subscriptions[1], later_sub)

# FORM TESTS
class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='formuser',
            password='TestPass123'
        )
        self.category = Category.objects.create(
            user=self.user,
            category_name='Food',
            type='expense'
        )

    def test_income_form_valid(self):
        form = IncomeForm(data={
            'amount': '1200.00',
            'category': self.category.id,
            'date': '2026-03-10',
            'description': 'Part-time job'
        })
        self.assertTrue(form.is_valid())

    def test_expense_form_valid(self):
        form = ExpenseForm(data={
            'amount': '20.50',
            'category': self.category.id,
            'date': '2026-03-11',
            'description': 'Lunch'
        })
        self.assertTrue(form.is_valid())

    def test_budget_limit_form_invalid_without_required_fields(self):
        form = BudgetLimitForm(data={
            'category': '',
            'limit_amount': '',
            'period': 'monthly',
            'warning_threshold': '80',
            'start_date': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
        self.assertIn('limit_amount', form.errors)
        self.assertIn('start_date', form.errors)

    def test_bill_form_valid(self):
        form = BillForm(data={
            'bill_name': 'Electricity',
            'amount': '60.00',
            'due_date': '2026-03-20',
            'is_recurring': True
        })
        self.assertTrue(form.is_valid())

    def test_income_form_invalid_without_amount(self):
        form = IncomeForm(data={
            'amount': '',
            'category': self.category.id,
            'date': '2026-03-10',
            'description': 'Part-time job'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_expense_form_invalid_without_date(self):
        form = ExpenseForm(data={
            'amount': '20.50',
            'category': self.category.id,
            'date': '',
            'description': 'Lunch'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_budget_limit_form_valid(self):
        form = BudgetLimitForm(data={
            'category': self.category.id,
            'limit_amount': '300.00',
            'period': 'monthly',
            'warning_threshold': '80',
            'start_date': '2026-03-01'
        })
        self.assertTrue(form.is_valid())

    def test_bill_form_invalid_without_bill_name(self):
        form = BillForm(data={
            'bill_name': '',
            'amount': '60.00',
            'due_date': '2026-03-20',
            'is_recurring': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('bill_name', form.errors)

# VIEW TESTS
class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password='TestPass123'
        )
        self.other_user = User.objects.create_user(
            username='bob',
            password='TestPass123'
        )

        self.expense_category = Category.objects.create(
            user=self.user,
            category_name='Food',
            type='expense'
        )
        self.income_category = Category.objects.create(
            user=self.user,
            category_name='Salary',
            type='income'
        )

        self.other_category = Category.objects.create(
            user=self.other_user,
            category_name='Other Food',
            type='expense'
        )

    def test_add_income_requires_login(self):
        response = self.client.get(reverse('add_income'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_add_expense_requires_login(self):
        response = self.client.get(reverse('add_expense'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_bill_list_requires_login(self):
        response = self.client.get(reverse('bill_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_subscription_list_requires_login(self):
        response = self.client.get(reverse('subscription_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_delete_income_owner_can_delete(self):
        income = Income.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=date.today()
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('delete_income', args=[income.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('income_list'))
        self.assertFalse(Income.objects.filter(id=income.id).exists())

    def test_delete_expense_owner_can_delete(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('50.00'),
            date=date.today()
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('delete_expense', args=[expense.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('expense_list'))
        self.assertFalse(Expense.objects.filter(id=expense.id).exists())

    def test_delete_bill_owner_can_delete(self):
        bill = Bill.objects.create(
            user=self.user,
            bill_name='Water',
            amount=Decimal('22.00'),
            due_date=date.today() + timedelta(days=5)
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('delete_bill', args=[bill.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('bill_list'))
        self.assertFalse(Bill.objects.filter(id=bill.id).exists())

    def test_delete_goal_owner_can_delete(self):
        goal = SavingsGoal.objects.create(
            user=self.user,
            goal_name='Holiday',
            target_amount=Decimal('1000.00'),
            current_amount=Decimal('100.00'),
            deadline=date.today() + timedelta(days=60)
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('delete_goal', args=[goal.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('savings_goals'))
        self.assertFalse(SavingsGoal.objects.filter(id=goal.id).exists())

    def test_delete_subscription_owner_can_delete(self):
        sub = Subscription.objects.create(
            user=self.user,
            subscription_name='Disney+',
            monthly_cost=Decimal('7.99'),
            billing_date=date.today(),
            status='active'
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('delete_subscription', args=[sub.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('subscription_list'))
        self.assertFalse(Subscription.objects.filter(id=sub.id).exists())

    def test_add_income_invalid_post_does_not_create_income(self):
        self.client.login(username='alice', password='TestPass123')

        response = self.client.post(reverse('add_income'), {
            'amount': '',
            'category': self.income_category.id,
            'date': '2026-03-10',
            'description': 'Salary'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Income.objects.count(), 0)

    def test_add_expense_invalid_post_does_not_create_expense(self):
        self.client.login(username='alice', password='TestPass123')

        response = self.client.post(reverse('add_expense'), {
            'amount': '',
            'category': self.expense_category.id,
            'date': '2026-03-11',
            'description': 'Groceries'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.count(), 0)

    def test_add_category_missing_name_does_not_create_category(self):
        self.client.login(username='alice', password='TestPass123')

        original_count = Category.objects.filter(user=self.user).count()

        response = self.client.post(reverse('add_category'), {
            'category_name': '',
            'type': 'expense',
            'description': 'Travel costs'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category_limits'))
        self.assertEqual(Category.objects.filter(user=self.user).count(), original_count)


    # Auth views
    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_post_creates_user_and_redirects(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_post_valid_user_redirects_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'alice',
            'password': 'TestPass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_logout_redirects_login(self):
        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


    # Protected views
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_authenticated_user_loads_correct_context(self):
        Income.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=date.today()
        )
        Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('200.00'),
            date=date.today()
        )

        Bill.objects.create(
            user=self.user,
            bill_name='Internet',
            amount=Decimal('30.00'),
            due_date=date.today() + timedelta(days=3)
        )

        BudgetLimit.objects.create(
            user=self.user,
            category=self.expense_category,
            limit_amount=Decimal('500.00'),
            period='monthly',
            warning_threshold=Decimal('80.00'),
            start_date=date.today().replace(day=1)
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertEqual(response.context['total_income'], Decimal('1000.00'))
        self.assertEqual(response.context['total_expense'], Decimal('200.00'))
        self.assertEqual(response.context['balance'], Decimal('800.00'))
        self.assertIn('chart_labels', response.context)
        self.assertIn('chart_data', response.context)


    # Income views
    def test_add_income_creates_income_for_logged_in_user(self):
        self.client.login(username='alice', password='TestPass123')

        response = self.client.post(reverse('add_income'), {
            'amount': '1500.00',
            'category': self.income_category.id,
            'date': '2026-03-10',
            'description': 'Salary'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(Income.objects.count(), 1)

        income = Income.objects.first()
        self.assertEqual(income.user, self.user)
        self.assertEqual(income.amount, Decimal('1500.00'))
        self.assertEqual(income.description, 'Salary')

    def test_income_list_shows_only_current_user_incomes(self):
        Income.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=date.today()
        )
        Income.objects.create(
            user=self.other_user,
            amount=Decimal('9999.00'),
            date=date.today()
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('income_list'))

        self.assertEqual(response.status_code, 200)
        incomes = list(response.context['incomes'])
        self.assertEqual(len(incomes), 1)
        self.assertEqual(incomes[0].user, self.user)

    def test_delete_income_only_owner_can_delete(self):
        income = Income.objects.create(
            user=self.user,
            category=self.income_category,
            amount=Decimal('1000.00'),
            date=date.today()
        )

        self.client.login(username='bob', password='TestPass123')
        response = self.client.get(reverse('delete_income', args=[income.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Income.objects.filter(id=income.id).exists())


    # Expense views
    def test_add_expense_creates_expense_for_logged_in_user(self):
        self.client.login(username='alice', password='TestPass123')

        response = self.client.post(reverse('add_expense'), {
            'amount': '45.50',
            'category': self.expense_category.id,
            'date': '2026-03-11',
            'description': 'Groceries'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(Expense.objects.count(), 1)

        expense = Expense.objects.first()
        self.assertEqual(expense.user, self.user)
        self.assertEqual(expense.amount, Decimal('45.50'))
        self.assertEqual(expense.description, 'Groceries')

    def test_expense_list_shows_only_current_user_expenses(self):
        Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('30.00'),
            date=date.today()
        )
        Expense.objects.create(
            user=self.other_user,
            category=self.other_category,
            amount=Decimal('500.00'),
            date=date.today()
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('expense_list'))

        self.assertEqual(response.status_code, 200)
        expenses = list(response.context['expenses'])
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].user, self.user)

    def test_delete_expense_only_owner_can_delete(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('50.00'),
            date=date.today()
        )

        self.client.login(username='bob', password='TestPass123')
        response = self.client.get(reverse('delete_expense', args=[expense.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Expense.objects.filter(id=expense.id).exists())


    # Category / budget limit views
    def test_add_category_creates_category(self):
        self.client.login(username='alice', password='TestPass123')

        response = self.client.post(reverse('add_category'), {
            'category_name': 'Transport',
            'type': 'expense',
            'description': 'Travel costs'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category_limits'))
        self.assertTrue(
            Category.objects.filter(
                user=self.user,
                category_name='Transport',
                type='expense'
            ).exists()
        )

    def test_category_limits_post_creates_budget_limit(self):
        self.client.login(username='alice', password='TestPass123')

        response = self.client.post(reverse('category_limits'), {
            'category': self.expense_category.id,
            'limit_amount': '300.00',
            'period': 'monthly',
            'warning_threshold': '80.00',
            'start_date': '2026-03-01'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category_limits'))
        self.assertEqual(BudgetLimit.objects.count(), 1)

        limit = BudgetLimit.objects.first()
        self.assertEqual(limit.user, self.user)
        self.assertEqual(limit.limit_amount, Decimal('300.00'))


    # Bill views
    def test_bill_list_post_creates_bill(self):
        self.client.login(username='alice', password='TestPass123')

        response = self.client.post(reverse('bill_list'), {
            'bill_name': 'Electricity',
            'amount': '75.00',
            'due_date': '2026-03-20',
            'is_recurring': True
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('bill_list'))
        self.assertEqual(Bill.objects.count(), 1)

        bill = Bill.objects.first()
        self.assertEqual(bill.user, self.user)
        self.assertEqual(bill.bill_name, 'Electricity')

    def test_delete_bill_only_owner_can_delete(self):
        bill = Bill.objects.create(
            user=self.user,
            bill_name='Water',
            amount=Decimal('22.00'),
            due_date=date.today() + timedelta(days=5)
        )

        self.client.login(username='bob', password='TestPass123')
        response = self.client.get(reverse('delete_bill', args=[bill.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Bill.objects.filter(id=bill.id).exists())


    # Search view
    def test_search_view_filters_by_type_and_amount(self):
        Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('10.00'),
            description='Snack',
            date=date(2026, 3, 10)
        )
        Expense.objects.create(
            user=self.user,
            category=self.expense_category,
            amount=Decimal('100.00'),
            description='Groceries',
            date=date(2026, 3, 11)
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('search'), {
            'type': 'expense',
            'amount_min': '50',
            'amount_max': '150'
        })

        self.assertEqual(response.status_code, 200)
        results = list(response.context['results'])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].amount, Decimal('100.00'))


    # Savings goals views
    def test_savings_goals_post_creates_goal(self):
        self.client.login(username='alice', password='TestPass123')

        response = self.client.post(reverse('savings_goals'), {
            'goal_name': 'New Laptop',
            'target_amount': '1200.00',
            'current_amount': '200.00',
            'deadline': '2026-06-01'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SavingsGoal.objects.count(), 1)

        goal = SavingsGoal.objects.first()
        self.assertEqual(goal.user, self.user)
        self.assertEqual(goal.goal_name, 'New Laptop')
        self.assertEqual(goal.current_amount, Decimal('200.00'))

    def test_delete_goal_only_owner_can_delete(self):
        goal = SavingsGoal.objects.create(
            user=self.user,
            goal_name='Holiday',
            target_amount=Decimal('1000.00'),
            current_amount=Decimal('100.00'),
            deadline=date.today() + timedelta(days=60)
        )

        self.client.login(username='bob', password='TestPass123')
        response = self.client.get(reverse('delete_goal', args=[goal.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(SavingsGoal.objects.filter(id=goal.id).exists())


    # Subscription views
    def test_subscription_list_post_creates_subscription(self):
        self.client.login(username='alice', password='TestPass123')

        response = self.client.post(reverse('subscription_list'), {
            'subscription_name': 'Netflix',
            'monthly_cost': '9.99',
            'billing_date': '2026-03-15',
            'status': 'active'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Subscription.objects.count(), 1)

        sub = Subscription.objects.first()
        self.assertEqual(sub.user, self.user)
        self.assertEqual(sub.subscription_name, 'Netflix')
        self.assertEqual(sub.monthly_cost, Decimal('9.99'))

    def test_subscription_total_monthly_only_counts_active(self):
        Subscription.objects.create(
            user=self.user,
            subscription_name='Netflix',
            monthly_cost=Decimal('9.99'),
            billing_date=date.today(),
            status='active'
        )
        Subscription.objects.create(
            user=self.user,
            subscription_name='Spotify',
            monthly_cost=Decimal('10.99'),
            billing_date=date.today(),
            status='paused'
        )

        self.client.login(username='alice', password='TestPass123')
        response = self.client.get(reverse('subscription_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['total_monthly'],
            Decimal('9.99')
        )

    def test_delete_subscription_only_owner_can_delete(self):
        sub = Subscription.objects.create(
            user=self.user,
            subscription_name='Disney+',
            monthly_cost=Decimal('7.99'),
            billing_date=date.today(),
            status='active'
        )

        self.client.login(username='bob', password='TestPass123')
        response = self.client.get(reverse('delete_subscription', args=[sub.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Subscription.objects.filter(id=sub.id).exists())
