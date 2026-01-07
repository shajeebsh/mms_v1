from django.db import migrations


def forwards_migrate_family_to_house(apps, schema_editor):
    Family = apps.get_model("membership", "Family")
    HouseRegistration = apps.get_model("membership", "HouseRegistration")
    MembershipDues = apps.get_model("membership", "MembershipDues")
    Payment = apps.get_model("membership", "Payment")

    db_alias = schema_editor.connection.alias

    # Create a 1:1 mapping Family.id -> HouseRegistration.id where possible.
    for family in Family.objects.using(db_alias).all().iterator():
        if HouseRegistration.objects.using(db_alias).filter(pk=family.pk).exists():
            house_id = family.pk
        else:
            house = HouseRegistration.objects.using(db_alias).create(
                id=family.pk,
                house_name=getattr(family, "name", "") or "",
                house_number="",
            )
            house_id = house.pk

        MembershipDues.objects.using(db_alias).filter(
            family_id=family.pk, house__isnull=True
        ).update(house_id=house_id)

        Payment.objects.using(db_alias).filter(
            family_id=family.pk, house__isnull=True
        ).update(house_id=house_id)


def backwards_migrate_house_to_family(apps, schema_editor):
    # Non-destructive no-op. (We keep created houses.)
    return


class Migration(migrations.Migration):

    dependencies = [
        ("membership", "0010_create_house_registration_and_add_house_fields"),
    ]

    operations = [
        migrations.RunPython(
            forwards_migrate_family_to_house, backwards_migrate_house_to_family
        ),
    ]
