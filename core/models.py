from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


def normalize_phone(value):
    digits = "".join(character for character in value if character.isdigit())
    if len(digits) == 11 and digits.startswith("8"):
        digits = f"7{digits[1:]}"
    return f"+{digits}" if digits else ""


def appointment_bounds(start_at, service):
    return start_at, start_at + timedelta(minutes=service.duration)


def master_can_provide_service(master, service):
    service_ids = master.services.values_list("id", flat=True)
    return not service_ids.exists() or service.pk in service_ids


def master_works_at(master, start_at, service):
    local_start = timezone.localtime(start_at)
    local_end = timezone.localtime(start_at + timedelta(minutes=service.duration))
    if local_start.date() != local_end.date():
        return False

    schedules = master.work_schedules.filter(
        is_active=True,
        weekday=local_start.weekday(),
        start_time__lte=local_start.time(),
        end_time__gte=local_end.time(),
    )
    return schedules.exists()


def master_has_overlap(master, start_at, service, exclude_pk=None):
    start_at, end_at = appointment_bounds(start_at, service)
    appointments = Appointment.objects.filter(master=master).exclude(status="cancelled")
    if exclude_pk:
        appointments = appointments.exclude(pk=exclude_pk)

    for appointment in appointments.select_related("service"):
        busy_start, busy_end = appointment_bounds(
            appointment.appointment_date,
            appointment.service,
        )
        if busy_start < end_at and start_at < busy_end:
            return True
    return False


def validate_appointment_slot(master, service, start_at, exclude_pk=None):
    if not master:
        return
    if not master.is_active:
        raise ValidationError("Выбранный специалист сейчас недоступен.")
    if not master_can_provide_service(master, service):
        raise ValidationError("Этот специалист не оказывает выбранную услугу.")
    if not master_works_at(master, start_at, service):
        raise ValidationError("Выбранное время не входит в рабочее расписание специалиста.")
    if master_has_overlap(master, start_at, service, exclude_pk=exclude_pk):
        raise ValidationError("Это время уже занято. Выбери другое время или специалиста.")


class Service(models.Model):
    title = models.CharField("Название", max_length=100)
    description = models.TextField("Описание")
    price = models.DecimalField(
        "Цена (руб)",
        max_digits=10,
        decimal_places=0,
        blank=True,
        null=True,
    )
    duration = models.PositiveIntegerField("Длительность (мин)", default=60)
    image = models.ImageField(
        "Изображение",
        upload_to="services/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Master(models.Model):
    first_name = models.CharField("Имя", max_length=50)
    last_name = models.CharField("Фамилия", max_length=50)
    specialty = models.CharField("Специальность", max_length=100)
    bio = models.TextField("О себе")
    experience = models.PositiveIntegerField("Опыт (лет)", default=0)
    photo = models.ImageField(
        "Фото",
        upload_to="masters/",
        blank=True,
        null=True,
    )
    services = models.ManyToManyField(
        Service,
        verbose_name="Услуги",
        related_name="masters",
        blank=True,
    )
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"
        ordering = ["last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class WorkSchedule(models.Model):
    WEEKDAY_CHOICES = [
        (0, "Понедельник"),
        (1, "Вторник"),
        (2, "Среда"),
        (3, "Четверг"),
        (4, "Пятница"),
        (5, "Суббота"),
        (6, "Воскресенье"),
    ]

    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        verbose_name="Мастер",
        related_name="work_schedules",
    )
    weekday = models.PositiveSmallIntegerField("День недели", choices=WEEKDAY_CHOICES)
    start_time = models.TimeField("Начало работы")
    end_time = models.TimeField("Окончание работы")
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        verbose_name = "Рабочее время"
        verbose_name_plural = "Рабочее время"
        ordering = ["master", "weekday", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["master", "weekday", "start_time", "end_time"],
                name="unique_master_work_interval",
            ),
            models.CheckConstraint(
                condition=Q(start_time__lt=models.F("end_time")),
                name="work_schedule_start_before_end",
            ),
        ]

    def __str__(self):
        return (
            f"{self.master} — {self.get_weekday_display()} "
            f"{self.start_time:%H:%M}-{self.end_time:%H:%M}"
        )


class Client(models.Model):
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20, unique=True)
    email = models.EmailField("Email", blank=True)
    birth_date = models.DateField("Дата рождения", blank=True, null=True)
    notes = models.TextField("Заметки", blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлен", auto_now=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает подтверждения"),
        ("confirmed", "Подтверждено"),
        ("completed", "Выполнено"),
        ("cancelled", "Отменено"),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        verbose_name="Клиент",
        related_name="appointments",
        blank=True,
        null=True,
    )
    client_name = models.CharField("Имя клиента", max_length=100)
    client_phone = models.CharField("Телефон", max_length=20)
    client_email = models.EmailField("Email", blank=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name="Услуга",
        related_name="appointments",
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.SET_NULL,
        verbose_name="Мастер",
        null=True,
        blank=True,
        related_name="appointments",
    )
    appointment_date = models.DateTimeField("Дата и время записи")
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ["-appointment_date"]

    def clean(self):
        super().clean()
        if self.appointment_date and self.service_id and self.master_id:
            validate_appointment_slot(
                self.master,
                self.service,
                self.appointment_date,
                exclude_pk=self.pk,
            )

    def __str__(self):
        return f"{self.client_name} — {self.service} ({self.appointment_date})"


class Review(models.Model):
    author_name = models.CharField("Имя автора", max_length=100)
    rating = models.PositiveIntegerField("Оценка", default=5)
    text = models.TextField("Текст отзыва")
    is_published = models.BooleanField("Опубликован", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author_name} — {self.rating}★"


class ContactMessage(models.Model):
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    message = models.TextField("Сообщение")
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.created_at}"
