from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("membership", "0011_migrate_family_to_house_registration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="membershipdues",
            name="house",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="membership_dues",
                to="membership.houseregistration",
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="house",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payments",
                to="membership.houseregistration",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="membershipdues",
            unique_together={("house", "year", "month")},
        ),
        migrations.AlterModelOptions(
            name="membershipdues",
            options={
                "ordering": ["-year", "-month", "house__house_name", "house__house_number"],
                "verbose_name": "Membership Due",
                "verbose_name_plural": "Membership Dues",
            },
        ),
        migrations.RemoveField(model_name="membershipdues", name="family"),
        migrations.RemoveField(model_name="payment", name="family"),
        migrations.DeleteModel(name="Family"),
    ]
