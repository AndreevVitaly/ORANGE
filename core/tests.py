from datetime import timedelta, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import AppointmentForm
from .models import Appointment, Client, ContactMessage, Master, Service, WorkSchedule


class PublicSiteTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            title="Классический массаж",
            description="Тестовое описание услуги",
            price=2500,
            duration=60,
        )
        self.master = Master.objects.create(
            first_name="Анна",
            last_name="Иванова",
            specialty="Массажист",
            bio="Описание специалиста",
            experience=5,
        )
        self.master.services.add(self.service)
        WorkSchedule.objects.create(
            master=self.master,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(18, 0),
        )

    def next_monday_at(self, hour, minute=0):
        now = timezone.localtime()
        days_ahead = (0 - now.weekday()) % 7
        if days_ahead == 0 and now.time() >= time(hour, minute):
            days_ahead = 7
        target_date = now.date() + timedelta(days=days_ahead)
        return timezone.make_aware(
            timezone.datetime.combine(target_date, time(hour, minute)),
            timezone.get_current_timezone(),
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
        self.assertContains(response, str(self.master))

    def test_appointment_is_saved(self):
        appointment_date = self.next_monday_at(10)
        response = self.client.post(
            reverse("core:appointment_create", args=[self.service.pk]),
            {
                "client_name": "Иван",
                "client_phone": "+7 900 000-00-00",
                "client_email": "ivan@example.com",
                "master": self.master.pk,
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
        appointment_date = self.next_monday_at(10)
        url = reverse("core:appointment_create", args=[self.service.pk])
        data = {
            "client_name": "Иван",
            "client_phone": "+7 900 000-00-00",
            "client_email": "",
            "master": self.master.pk,
            "appointment_date": appointment_date.strftime("%Y-%m-%dT%H:%M"),
            "comment": "",
        }

        self.client.post(url, data)
        data["client_phone"] = "8 (900) 000-00-00"
        data["appointment_date"] = (appointment_date + timedelta(hours=2)).strftime(
            "%Y-%m-%dT%H:%M"
        )
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

    def test_appointment_rejects_busy_slot(self):
        appointment_date = self.next_monday_at(10)
        Appointment.objects.create(
            client_name="Анна",
            client_phone="+79001112233",
            service=self.service,
            master=self.master,
            appointment_date=appointment_date,
            status="confirmed",
        )

        form = AppointmentForm(
            data={
                "client_name": "Иван",
                "client_phone": "+7 900 000-00-00",
                "client_email": "",
                "master": self.master.pk,
                "appointment_date": (appointment_date + timedelta(minutes=30)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
                "comment": "",
            },
            service=self.service,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("Это время уже занято", str(form.errors))

    def test_appointment_rejects_non_working_time(self):
        appointment_date = self.next_monday_at(20)
        form = AppointmentForm(
            data={
                "client_name": "Иван",
                "client_phone": "+7 900 000-00-00",
                "client_email": "",
                "master": self.master.pk,
                "appointment_date": appointment_date.strftime("%Y-%m-%dT%H:%M"),
                "comment": "",
            },
            service=self.service,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("рабочее расписание", str(form.errors))

    def test_master_list_is_filtered_by_service(self):
        other_service = Service.objects.create(
            title="Йога",
            description="Описание",
            duration=60,
        )
        form = AppointmentForm(service=other_service)

        self.assertNotIn(self.master, form.fields["master"].queryset)

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


class CrmPanelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin",
            password="password",
            is_staff=True,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("crm:dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("crm:login"), response.url)

    def test_dashboard_is_available_for_user(self):
        self.client.login(username="admin", password="password")
        response = self.client.get(reverse("crm:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Дашборд")

    def test_client_list_is_available_for_user(self):
        self.client.login(username="admin", password="password")
        response = self.client.get(reverse("crm:clients"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Клиенты")
