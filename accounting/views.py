from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from .models import Account, AccountCategory, JournalEntry


@login_required
def chart_of_accounts_view(request):
    """Display Chart of Accounts grouped by category type in tabular format"""
    category_types = [
        ('asset', 'Assets'),
        ('liability', 'Liabilities'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expenses'),
    ]

    accounts_by_category = {}

    for cat_type, cat_label in category_types:
        accounts = Account.objects.filter(
            category__category_type=cat_type,
            is_active=True
        ).select_related('category').order_by('code')

        accounts_with_balance = []
        for account in accounts:
            debit_total = JournalEntry.objects.filter(account=account).aggregate(
                total=Sum('debit')
            )['total'] or 0
            credit_total = JournalEntry.objects.filter(account=account).aggregate(
                total=Sum('credit')
            )['total'] or 0

            if cat_type in ('asset', 'expense'):
                balance = debit_total - credit_total
            else:
                balance = credit_total - debit_total

            accounts_with_balance.append({
                'account': account,
                'debit_total': debit_total,
                'credit_total': credit_total,
                'balance': balance,
            })

        accounts_by_category[cat_label] = {
            'type': cat_type,
            'accounts': accounts_with_balance,
            'total_balance': sum(a['balance'] for a in accounts_with_balance),
        }

    context = {
        'accounts_by_category': accounts_by_category,
        'page_title': 'Chart of Accounts',
    }

    return render(request, 'accounting/chart_of_accounts.html', context)
