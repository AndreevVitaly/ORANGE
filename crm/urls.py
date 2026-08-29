from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "crm"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="crm/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="core:index"), name="logout"),
    path("appointments/", views.appointment_list, name="appointments"),
    path(
        "appointments/<int:pk>/status/",
        views.appointment_update_status,
        name="appointment_update_status",
    ),
    path("clients/", views.client_list, name="clients"),
    path("clients/<int:pk>/", views.client_detail, name="client_detail"),
]
