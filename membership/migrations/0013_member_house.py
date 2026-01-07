from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("membership", "0012_remove_family_and_enforce_house"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="house",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="members",
                to="membership.houseregistration",
            ),
        ),
    ]
