import django.db.models.deletion
from django.db import migrations, models


def normalize_phone(value):
    digits = "".join(character for character in value if character.isdigit())
    if len(digits) == 11 and digits.startswith("8"):
        digits = f"7{digits[1:]}"
    return f"+{digits}" if digits else ""


def create_clients_for_existing_appointments(apps, schema_editor):
    Appointment = apps.get_model("core", "Appointment")
    Client = apps.get_model("core", "Client")

    for appointment in Appointment.objects.all().iterator():
        phone = normalize_phone(appointment.client_phone)
        if not phone:
            phone = f"unknown-{appointment.pk}"

        client, _ = Client.objects.get_or_create(
            phone=phone,
            defaults={
                "name": appointment.client_name,
                "email": appointment.client_email,
            },
        )
        appointment.client_id = client.pk
        appointment.client_phone = phone
        appointment.save(update_fields=["client", "client_phone"])


def unlink_clients(apps, schema_editor):
    Appointment = apps.get_model("core", "Appointment")
    Appointment.objects.update(client=None)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
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
                ("name", models.CharField(max_length=100, verbose_name="Имя")),
                (
                    "phone",
                    models.CharField(
                        max_length=20,
                        unique=True,
                        verbose_name="Телефон",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        verbose_name="Email",
                    ),
                ),
                (
                    "birth_date",
                    models.DateField(
                        blank=True,
                        null=True,
                        verbose_name="Дата рождения",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Заметки")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создан"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Обновлен"),
                ),
            ],
            options={
                "verbose_name": "Клиент",
                "verbose_name_plural": "Клиенты",
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="appointment",
            name="client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="appointments",
                to="core.client",
                verbose_name="Клиент",
            ),
        ),
        migrations.RunPython(
            create_clients_for_existing_appointments,
            unlink_clients,
        ),
    ]
