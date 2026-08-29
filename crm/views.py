from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.models import Appointment, Client, ContactMessage, Master, Service


@login_required
def dashboard(request):
    today = timezone.localdate()
    appointments = Appointment.objects.select_related(
        "client",
        "service",
        "master",
    )
    context = {
        "pending_count": appointments.filter(status="pending").count(),
        "today_count": appointments.filter(appointment_date__date=today).count(),
        "clients_count": Client.objects.count(),
        "messages_count": ContactMessage.objects.filter(is_read=False).count(),
        "latest_appointments": appointments[:8],
        "latest_clients": Client.objects.order_by("-created_at")[:5],
        "services_count": Service.objects.filter(is_active=True).count(),
        "masters_count": Master.objects.filter(is_active=True).count(),
    }
    return render(request, "crm/dashboard.html", context)


@login_required
def appointment_list(request):
    status = request.GET.get("status", "")
    appointments = Appointment.objects.select_related("client", "service", "master")
    if status:
        appointments = appointments.filter(status=status)
    return render(
        request,
        "crm/appointment_list.html",
        {
            "appointments": appointments,
            "status": status,
            "status_choices": Appointment.STATUS_CHOICES,
        },
    )


@login_required
def appointment_update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        status = request.POST.get("status")
        allowed_statuses = dict(Appointment.STATUS_CHOICES)
        if status in allowed_statuses:
            appointment.status = status
            appointment.save(update_fields=["status", "updated_at"])
            messages.success(request, "Статус записи обновлен.")
        else:
            messages.error(request, "Неизвестный статус записи.")
    return redirect("crm:appointments")


@login_required
def client_list(request):
    query = request.GET.get("q", "").strip()
    clients = Client.objects.all()
    if query:
        clients = clients.filter(name__icontains=query) | clients.filter(phone__icontains=query)
    return render(request, "crm/client_list.html", {"clients": clients, "query": query})


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    appointments = client.appointments.select_related("service", "master")
    return render(
        request,
        "crm/client_detail.html",
        {"client_item": client, "appointments": appointments},
    )
