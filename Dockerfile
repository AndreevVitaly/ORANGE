# Используем официальный образ Python
FROM python:3.14-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Рабочая директория
WORKDIR /app

# Устанавливаем системные зависимости для psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY ./ORANGE/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем проект
COPY ./ORANGE /app

# Копируем и делаем исполняемым entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Создаём директорию для статики и медиа
RUN mkdir -p /app/staticfiles /app/media

# Открываем порт
EXPOSE 8000

# Запускаем entrypoint
ENTRYPOINT ["/entrypoint.sh"]
