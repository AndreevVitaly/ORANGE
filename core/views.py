from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AppointmentForm, ContactMessageForm
from .models import Client, Master, Service, normalize_phone


def index(request):
    services = Service.objects.filter(is_active=True)[:6]
    masters = Master.objects.filter(is_active=True)[:3]
    context = {
        "services": services,
        "masters": masters,
        "contact_form": ContactMessageForm(),
    }
    return render(request, "core/index.html", context)


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)
    masters = service.masters.filter(is_active=True)
    return render(
        request,
        "core/service_detail.html",
        {"service": service, "masters": masters},
    )


def appointment_create(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)

    if request.method == "POST":
        form = AppointmentForm(request.POST, service=service)
        if form.is_valid():
            with transaction.atomic():
                phone = normalize_phone(form.cleaned_data["client_phone"])
                client, created = Client.objects.get_or_create(
                    phone=phone,
                    defaults={
                        "name": form.cleaned_data["client_name"],
                        "email": form.cleaned_data["client_email"],
                    },
                )
                if not created:
                    changed_fields = []
                    if client.name != form.cleaned_data["client_name"]:
                        client.name = form.cleaned_data["client_name"]
                        changed_fields.append("name")
                    email = form.cleaned_data["client_email"]
                    if email and client.email != email:
                        client.email = email
                        changed_fields.append("email")
                    if changed_fields:
                        client.save(update_fields=[*changed_fields, "updated_at"])

                appointment = form.save(commit=False)
                appointment.client = client
                appointment.client_phone = phone
                appointment.service = service
                appointment.full_clean()
                appointment.save()
            messages.success(
                request,
                "Заявка отправлена. Мы свяжемся с тобой для подтверждения записи.",
            )
            return redirect("core:appointment_success")
    else:
        form = AppointmentForm(service=service)

    return render(
        request,
        "core/appointment_form.html",
        {"service": service, "form": form},
    )


def appointment_success(request):
    return render(request, "core/appointment_success.html")


def contact_message_create(request):
    if request.method != "POST":
        return redirect("core:index")

    form = ContactMessageForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Сообщение отправлено. Спасибо!")
    else:
        messages.error(request, "Проверь заполнение формы и попробуй еще раз.")

    return redirect("core:index")
