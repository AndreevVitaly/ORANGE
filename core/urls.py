from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("services/<int:pk>/", views.service_detail, name="service_detail"),
    path(
        "services/<int:pk>/appointment/",
        views.appointment_create,
        name="appointment_create",
    ),
    path(
        "appointment/success/",
        views.appointment_success,
        name="appointment_success",
    ),
    path("contact/", views.contact_message_create, name="contact_message_create"),
]
