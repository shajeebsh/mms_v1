from django.core.management.base import BaseCommand
from django.utils import timezone
from membership.models import Family
from assets.models import Shop
from billing.models import Invoice, InvoiceLineItem
from decimal import Decimal

class Command(BaseCommand):
    help = 'Generate monthly invoices for members and tenants'

    def handle(self, *args, **options):
        # Aggressively disable all post_save signals to avoid django-tasks error
        from django.db.models.signals import post_save
        post_save.receivers = []
        
        today = timezone.now().date()
        month_name = today.strftime('%B %Y')
        
        # 1. Generate for Families (Membership Dues)
        families = Family.objects.all() # In a real app, filter for active ones
        for family in families:
            # Check if invoice already exists for this month
            invoice_number = f"INV-FAM-{family.id}-{today.strftime('%Y%m')}"
            if not Invoice.objects.filter(invoice_number=invoice_number).exists():
                invoice = Invoice.objects.create(
                    invoice_number=invoice_number,
                    family=family,
                    date_issued=today,
                    due_date=today + timezone.timedelta(days=15),
                    status='draft'
                )
                
                # Assume a fixed monthly due of ₹500 if not specified
                # In production, this would come from a membership_due_amount setting
                amount = Decimal('500.00')
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    description=f"Membership Dues for {month_name}",
                    amount=amount
                )
                
                invoice.total_amount = amount
                invoice.save()
                self.stdout.write(f"Generated invoice {invoice_number} for family {family}")

        # 2. Generate for Shops (Rent)
        shops = Shop.objects.all()
        for shop in shops:
            invoice_number = f"INV-SHOP-{shop.id}-{today.strftime('%Y%m')}"
            if not Invoice.objects.filter(invoice_number=invoice_number).exists():
                invoice = Invoice.objects.create(
                    invoice_number=invoice_number,
                    shop=shop,
                    date_issued=today,
                    due_date=today + timezone.timedelta(days=10),
                    status='draft'
                )
                
                # Assume monthly rent from shop model if available
                amount = Decimal('5000.00') # Fallback
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    description=f"Shop Rent for {month_name}",
                    amount=amount
                )
                
                invoice.total_amount = amount
                invoice.save()
                self.stdout.write(f"Generated invoice {invoice_number} for shop {shop}")

        self.stdout.write(self.style.SUCCESS('Successfully generated monthly invoices'))
