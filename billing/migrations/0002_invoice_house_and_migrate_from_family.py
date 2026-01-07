from django.db import migrations, models
from django.db.models import F
import django.db.models.deletion


def forwards_invoice_family_to_house(apps, schema_editor):
    Invoice = apps.get_model("billing", "Invoice")

    db_alias = schema_editor.connection.alias

    # We created HouseRegistration with matching PKs in membership migration 0011.
    # So invoices can be relinked by copying family_id -> house_id.
    Invoice.objects.using(db_alias).filter(
        house__isnull=True, family__isnull=False
    ).update(house_id=F("family_id"))


def backwards_invoice_house_to_family(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ("membership", "0011_migrate_family_to_house_registration"),
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="house",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="invoices",
                to="membership.houseregistration",
            ),
        ),
        migrations.RunPython(forwards_invoice_family_to_house, backwards_invoice_house_to_family),
        migrations.RemoveField(model_name="invoice", name="family"),
    ]
