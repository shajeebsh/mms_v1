from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("membership", "0009_add_dropdown_fields_parallel"),
    ]

    operations = [
        migrations.CreateModel(
            name="HouseRegistration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("house_name", models.CharField(blank=True, max_length=200)),
                ("house_number", models.CharField(blank=True, max_length=50)),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "city",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="membership.city",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="membership.country",
                    ),
                ),
                (
                    "postal_code",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="membership.postalcode",
                    ),
                ),
                (
                    "state",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="membership.state",
                    ),
                ),
                (
                    "taluk",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="membership.taluk",
                    ),
                ),
                (
                    "ward",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="membership.ward",
                    ),
                ),
            ],
            options={
                "verbose_name": "House Registration",
                "verbose_name_plural": "House Registrations",
            },
        ),
        migrations.AddField(
            model_name="membershipdues",
            name="house",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="membership_dues",
                to="membership.houseregistration",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="house",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payments",
                to="membership.houseregistration",
            ),
        ),
    ]
