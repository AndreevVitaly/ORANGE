# 🍊 Апельсин — Оздоровительный центр

Сайт и CRM-система для оздоровительного центра «Апельсин» в г. Выборг.

**Адрес:** Ленинградская область, г. Выборг, ул. Крепостная  
**Телефон:** [+7 (921) 878-92-97](tel:+79218789297)

---

## Стек технологий

- **Backend:** Django 5.2 + Python 3.14
- **Frontend:** Django Templates + Bootstrap 5.3
- **База данных:** PostgreSQL 17 (production) / SQLite 3 (dev)
- **Контейнеризация:** Docker + Docker Compose
- **Reverse proxy:** Nginx
- **Кэш:** Redis 7
- **CI/CD:** GitHub

---

## Структура проекта

```
ORANGE/
├── config/           # Настройки Django (settings, urls, wsgi)
├── core/             # Основное приложение (модели, views, templates, static)
│   ├── models.py     # Service, Master, Appointment, Review, ContactMessage
│   ├── static/       # CSS, изображения, фавиконка
│   └── templates/    # HTML-шаблоны (base.html, index.html)
├── api/              # REST API (в разработке)
├── crm/              # CRM-панель (в разработке)
├── docker-compose.yml
├── docker-compose.dev.yml
├── Dockerfile
├── nginx.conf
└── requirements.txt
```

---

## Запуск локально (без Docker)

```cmd
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Сайт доступен по `http://127.0.0.1:8000/`

---

## Запуск через Docker

### Локальная разработка (SQLite)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

### Production (PostgreSQL)

```bash
docker compose up -d --build
```

---

## Основные модели

| Модель | Описание |
|--------|----------|
| `Service` | Услуги (йога, массаж, фитнес и т.д.) |
| `Master` | Специалисты центра |
| `Appointment` | Записи клиентов |
| `Review` | Отзывы |
| `ContactMessage` | Сообщения из формы обратной связи |

---

## Журнал изменений

### 05.04.2026

- ✅ Заменён номер телефона на **+7 (921) 878-92-97**
- ✅ Обновлён адрес: **г. Выборг, ул. Крепостная**
- ✅ Добавлены изображения йоги и массажа на главную
- ✅ Карточки услуг с полноэкранным изображением и градиентом
- ✅ Адаптивные стили для мобильных устройств
- ✅ Кнопки соцсетей (VK, Telegram, WhatsApp) — белый фон с оранжевым контуром
- ✅ Фавиконка — логотип апельсина
- ✅ Логотип в навигации и футере заменён с эмодзи на изображение
- ✅ Добавлен Nginx с правильными MIME-types для статики
- ✅ Docker-конфигурация для разработки и production

### 04.04.2026

- ✅ Инициализация проекта Django
- ✅ Создание моделей и миграций
- ✅ Базовый лендинг с Bootstrap
- ✅ Docker + Nginx + PostgreSQL + Redis

---

## Репозиторий

GitHub: https://github.com/AndreevVitaly/ORANGE

---

## Заметки

Дата начала: 02.04.2026
