from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Appointment, ContactMessage, Master


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateTimeField(
        label="Желаемые дата и время",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
    )

    class Meta:
        model = Appointment
        fields = [
            "client_name",
            "client_phone",
            "client_email",
            "master",
            "appointment_date",
            "comment",
        ]
        labels = {
            "client_name": "Ваше имя",
            "client_phone": "Телефон",
            "client_email": "Email",
            "master": "Специалист",
            "comment": "Комментарий",
        }
        widgets = {
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "client_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "tel",
                    "placeholder": "+7 (___) ___-__-__",
                }
            ),
            "client_email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Необязательно"}
            ),
            "master": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["master"].queryset = Master.objects.filter(is_active=True)
        self.fields["master"].required = False
        self.fields["master"].empty_label = "Подберем специалиста"

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data["appointment_date"]
        if appointment_date <= timezone.now():
            raise ValidationError("Выбери дату и время в будущем.")
        return appointment_date


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ваше имя"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "tel",
                    "placeholder": "Ваш телефон",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email (необязательно)"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Ваше сообщение",
                }
            ),
        }
