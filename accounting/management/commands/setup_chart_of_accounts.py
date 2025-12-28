from django.core.management.base import BaseCommand
from accounting.models import Account, AccountCategory
from django.db.models.signals import post_save

class Command(BaseCommand):
    help = 'Initialize Chart of Accounts with standard mosque accounts'

    def handle(self, *args, **options):
        # Aggressively disable all post_save signals to avoid django-tasks error
        from django.db.models.signals import post_save
        post_save.receivers = []
        self.stdout.write("All post_save signals temporarily disabled for setup.")

        # 1. Categories
        assets, _ = AccountCategory.objects.get_or_create(name='Assets', category_type='asset')
        liabi, _ = AccountCategory.objects.get_or_create(name='Liabilities', category_type='liability')
        equity, _ = AccountCategory.objects.get_or_create(name='Equity', category_type='equity')
        revenue, _ = AccountCategory.objects.get_or_create(name='Revenue', category_type='revenue')
        expense, _ = AccountCategory.objects.get_or_create(name='Expenses', category_type='expense')

        # 2. Accounts
        accounts = [
            {'code': '1001', 'name': 'Main Cash', 'category': assets},
            {'code': '1002', 'name': 'Bank Account', 'category': assets},
            {'code': '4001', 'name': 'Donations Revenue', 'category': revenue},
            {'code': '4002', 'name': 'Membership Dues Revenue', 'category': revenue},
            {'code': '4003', 'name': 'Asset Rental Revenue', 'category': revenue},
            {'code': '5001', 'name': 'General Expenses', 'category': expense},
            {'code': '5002', 'name': 'Utility Expenses', 'category': expense},
            {'code': '5003', 'name': 'Salary Expenses', 'category': expense},
        ]

        for acc_data in accounts:
            acc, created = Account.objects.get_or_create(code=acc_data['code'], defaults=acc_data)
            if created:
                self.stdout.write(f"Created account: {acc}")
            else:
                self.stdout.write(f"Account already exists: {acc}")

        self.stdout.write(self.style.SUCCESS('Successfully initialized Chart of Accounts'))
