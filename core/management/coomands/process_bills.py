from django.core.management.base import BaseCommand
from core.models import Bill, Expense
import datetime


class Command(BaseCommand):
    help = 'Auto process recurring bills on due date'

    def handle(self, *args, **kwargs):
        today = datetime.date.today()
        self.stdout.write(
            f'Processing bills for {today}...')

        # get all recurring bills due today
        bills_due = Bill.objects.filter(
            due_date=today,
            is_recurring=True
        )

        count = 0
        for bill in bills_due:
            # check if expense already created today
            already_exists = Expense.objects.filter(
                user=bill.user,
                amount=bill.amount,
                date=today,
                description=f'Auto Bill: {bill.bill_name}'
            ).exists()

            if not already_exists:
                # create expense automatically
                Expense.objects.create(
                    user=bill.user,
                    amount=bill.amount,
                    description=f'Auto Bill: {bill.bill_name}',
                    date=today
                )

                # update next due date for next month
                if bill.due_date.month == 12:
                    next_due = bill.due_date.replace(
                        year=bill.due_date.year + 1,
                        month=1
                    )
                else:
                    next_due = bill.due_date.replace(
                        month=bill.due_date.month + 1
                    )
                bill.due_date = next_due
                bill.save()
                count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {count} bills!'
            )
        )