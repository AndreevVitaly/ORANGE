# Инструкция по настройке HTTPS для 47appelsin.ru

## Предварительные требования

1. ✅ Домен `47appelsin.ru` привязан к серверу `72.56.249.17`
   - Проверить: `nslookup 47appelsin.ru`
   - Должен вернуть: `72.56.249.17`

2. ✅ На сервере открыты порты:
   - `80` (HTTP) — для валидации Let's Encrypt
   - `443` (HTTPS) — для защищённого соединения

3. ✅ Файл `.env` создан и заполнен на основе `.env.example`

---

## Шаг 1: Загрузка файлов на сервер

Скопируйте проект на сервер:

```bash
# На локальной машине
scp -r c:\DjangoProject\ORANGE user@72.56.249.17:/path/to/project
```

Или используйте git:

```bash
# На сервере
cd /path/to/project
git clone <your-repo-url>
cd ORANGE
```

---

## Шаг 2: Настройка окружения

```bash
# На сервере
cd /path/to/ORANGE

# Создаём .env из примера
cp .env.example .env

# Редактируем .env
nano .env
```

**Обязательные изменения в `.env`:**
```env
DJANGO_SECRET_KEY=<сгенерируйте новый ключ>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=47appelsin.ru,www.47appelsin.ru,72.56.249.17

POSTGRES_USER=apelsin
POSTGRES_PASSWORD=<ваш_надёжный_пароль>
POSTGRES_DB=apelsin_db
```

---

## Шаг 3: Получение SSL-сертификата

```bash
# На сервере
cd /path/to/ORANGE

# Делаем скрипт исполняемым
chmod +x scripts/init-letsencrypt.sh

# Запускаем скрипт
./scripts/init-letsencrypt.sh
```

Скрипт автоматически:
1. Запустит все сервисы
2. Временно отключит SSL для валидации
3. Получит сертификат от Let's Encrypt
4. Включит HTTPS и редирект с HTTP

---

## Шаг 4: Проверка работы

```bash
# Проверка HTTP (должен редиректить на HTTPS)
curl -I http://47appelsin.ru

# Проверка HTTPS
curl -I https://47appelsin.ru

# Проверка SSL-сертификата
echo | openssl s_client -servername 47appelsin.ru -connect 47appelsin.ru:443 2>/dev/null | openssl x509 -noout -dates
```

---

## Шаг 5: Автоматическое обновление сертификата

Certbot уже настроен на автоматическое обновление каждые 12 часов.

**Ручное обновление (если нужно):**

```bash
docker compose run --rm certbot renew
docker compose restart nginx
```

---

## Решение проблем

### DNS не распространился

```bash
# Проверка DNS через публичный сервер
nslookup 47appelsin.ru 8.8.8.8

# Или через онлайн-сервис
curl https://dns.google/resolve?name=47appelsin.ru&type=A
```

### Порт 80/443 закрыт

```bash
# Проверка открытых портов
sudo ss -tlnp | grep -E ':(80|443)'

# Если используете ufw
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Если используете firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Ошибка при получении сертификата

```bash
# Посмотреть логи certbot
docker compose logs certbot

# Посмотреть логи nginx
docker compose logs nginx

# Удалить и получить заново
docker compose down -v
./scripts/init-letsencrypt.sh
```

---

## Итоговая архитектура

```
Пользователь
    ↓
http://47appelsin.ru  (порт 80)
    ↓ редирект 301
https://47appelsin.ru (порт 443, SSL/TLS)
    ↓
    Nginx (обратный прокси)
    ↓
    Django (Gunicorn, порт 8000)
    ↓
    PostgreSQL
```
