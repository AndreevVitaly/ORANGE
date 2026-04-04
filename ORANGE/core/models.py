from django.db import models
from django.contrib.auth.models import User


class Service(models.Model):
    """Модель услуги"""
    title = models.CharField('Название', max_length=100)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена (руб)', max_digits=10, decimal_places=0, blank=True, null=True)
    duration = models.PositiveIntegerField('Длительность (мин)', default=60)
    image = models.ImageField('Изображение', upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['title']
    
    def __str__(self):
        return self.title


class Master(models.Model):
    """Модель мастера/специалиста"""
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    specialty = models.CharField('Специальность', max_length=100)
    bio = models.TextField('О себе')
    experience = models.PositiveIntegerField('Опыт (лет)', default=0)
    photo = models.ImageField('Фото', upload_to='masters/', blank=True, null=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'
        ordering = ['last_name']
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Appointment(models.Model):
    """Модель записи клиента"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('completed', 'Выполнено'),
        ('cancelled', 'Отменено'),
    ]
    
    client_name = models.CharField('Имя клиента', max_length=100)
    client_phone = models.CharField('Телефон', max_length=20)
    client_email = models.EmailField('Email', blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга', related_name='appointments')
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, verbose_name='Мастер', null=True, blank=True, related_name='appointments')
    appointment_date = models.DateTimeField('Дата и время записи')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    
    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f'{self.client_name} — {self.service} ({self.appointment_date})'


class Review(models.Model):
    """Модель отзыва"""
    author_name = models.CharField('Имя автора', max_length=100)
    rating = models.PositiveIntegerField('Оценка', default=5)
    text = models.TextField('Текст отзыва')
    is_published = models.BooleanField('Опубликован', default=False)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.author_name} — {self.rating}★'


class ContactMessage(models.Model):
    """Модель сообщения из формы обратной связи"""
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True)
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} — {self.created_at}'
