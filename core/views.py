from django.shortcuts import render
from .models import Service, Master


def index(request):
    """Главная страница сайта"""
    services = Service.objects.filter(is_active=True)[:6]
    masters = Master.objects.filter(is_active=True)[:3]
    
    context = {
        'services': services,
        'masters': masters,
    }
    
    return render(request, 'core/index.html', context)
