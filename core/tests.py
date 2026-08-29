from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Appointment, Client, ContactMessage, Service


class PublicSiteTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            title="Классический массаж",
            description="Тестовое описание услуги",
            price=2500,
            duration=60,
        )

    def test_index_displays_active_service(self):
        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.title)

    def test_index_hides_inactive_service(self):
        self.service.is_active = False
        self.service.save()

        response = self.client.get(reverse("core:index"))

        self.assertNotContains(response, self.service.title)

    def test_service_detail_is_available(self):
        response = self.client.get(
            reverse("core:service_detail", args=[self.service.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.description)

    def test_appointment_is_saved(self):
        appointment_date = timezone.localtime() + timedelta(days=2)
        response = self.client.post(
            reverse("core:appointment_create", args=[self.service.pk]),
            {
                "client_name": "Иван",
                "client_phone": "+7 900 000-00-00",
                "client_email": "ivan@example.com",
                "master": "",
                "appointment_date": appointment_date.strftime("%Y-%m-%dT%H:%M"),
                "comment": "Позвонить вечером",
            },
        )

        self.assertRedirects(response, reverse("core:appointment_success"))
        self.assertEqual(Appointment.objects.count(), 1)
        appointment = Appointment.objects.get()
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.client.phone, "+79000000000")
        self.assertEqual(Client.objects.count(), 1)

    def test_repeat_appointment_reuses_client(self):
        appointment_date = timezone.localtime() + timedelta(days=2)
        url = reverse("core:appointment_create", args=[self.service.pk])
        data = {
            "client_name": "Иван",
            "client_phone": "+7 900 000-00-00",
            "client_email": "",
            "master": "",
            "appointment_date": appointment_date.strftime("%Y-%m-%dT%H:%M"),
            "comment": "",
        }

        self.client.post(url, data)
        data["client_phone"] = "8 (900) 000-00-00"
        data["appointment_date"] = (
            appointment_date + timedelta(days=1)
        ).strftime("%Y-%m-%dT%H:%M")
        self.client.post(url, data)

        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(Appointment.objects.count(), 2)

    def test_past_appointment_is_rejected(self):
        appointment_date = timezone.localtime() - timedelta(days=1)
        response = self.client.post(
            reverse("core:appointment_create", args=[self.service.pk]),
            {
                "client_name": "Иван",
                "client_phone": "+7 900 000-00-00",
                "appointment_date": appointment_date.strftime("%Y-%m-%dT%H:%M"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Выбери дату и время в будущем.")
        self.assertFalse(Appointment.objects.exists())

    def test_contact_message_is_saved(self):
        response = self.client.post(
            reverse("core:contact_message_create"),
            {
                "name": "Анна",
                "phone": "+7 900 111-22-33",
                "email": "",
                "message": "Хочу узнать о расписании",
            },
        )

        self.assertRedirects(response, reverse("core:index"))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_crm_login_page_is_available(self):
        response = self.client.get(reverse("crm:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вход для сотрудников")
