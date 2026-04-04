from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'crm'

urlpatterns = [
    # CRM маршруты будут добавлены позже
    path('login/', auth_views.LoginView.as_view(template_name='crm/login.html'), name='login'),
]
