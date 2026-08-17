from django.db import migrations


def seed_statuses(apps, schema_editor):
    ReservationStatus = apps.get_model("reservation_app", "ReservationStatus")
    defaults = [
        ("Pending", "Reservation is awaiting confirmation"),
        ("Confirmed", "Reservation is confirmed"),
        ("Cancelled", "Reservation was cancelled"),
        ("Completed", "Reservation was completed"),
    ]
    for name, description in defaults:
        ReservationStatus.objects.get_or_create(
            name=name,
            defaults={"description": description},
        )


def unseed_statuses(apps, schema_editor):
    ReservationStatus = apps.get_model("reservation_app", "ReservationStatus")
    ReservationStatus.objects.filter(
        name__in=["Pending", "Confirmed", "Cancelled", "Completed"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("reservation_app", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_statuses, unseed_statuses),
    ]
