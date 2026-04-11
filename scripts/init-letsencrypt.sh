#!/bin/bash
# Скрипт для получения и обновления SSL-сертификата Let's Encrypt

set -e

DOMAIN="47appelsin.ru"
EMAIL="admin@47appelsin.ru"  # Замените на ваш email

echo "=== Шаг 1: Подготовка временной конфигурации ==="

# Создаем временный файл nginx.conf без SSL
cat > nginx-ssl-temp.conf <<'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    upstream django {
        server django:8000;
    }

    server {
        listen 80;
        server_name 47appelsin.ru www.47appelsin.ru;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

echo "=== Шаг 2: Запуск сервисов ==="

# Запускаем все сервисы
docker compose -f docker-compose.yml up -d

echo "=== Шаг 3: Временная замена nginx.conf для получения сертификата ==="

# Заменяем nginx.conf на временный (без SSL)
cp nginx.conf nginx-https-backup.conf
cp nginx-ssl-temp.conf nginx.conf

# Перезапускаем nginx
docker compose -f docker-compose.yml up -d --force-recreate nginx

echo "=== Шаг 4: Получение SSL-сертификата ==="

# Ждем чтобы nginx успел стартовать
sleep 3

# Получаем сертификат
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d "$DOMAIN" \
  -d "www.$DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --non-interactive \
  --keep-until-expiring

echo "=== Шаг 5: Восстановление основной конфигурации с HTTPS ==="

# Восстанавливаем nginx.conf с SSL
cp nginx-https-backup.conf nginx.conf

# Перезапускаем nginx
docker compose -f docker-compose.yml up -d --force-recreate nginx

# Удаляем временные файлы
rm -f nginx-ssl-temp.conf nginx-https-backup.conf

echo ""
echo "========================================="
echo "✅ Сертификат успешно установлен!"
echo "========================================="
echo "Сайт доступен по: https://$DOMAIN"
echo "HTTP автоматически перенаправляется на HTTPS"
