# PodmefomCloud API

API для музыкального сервиса PodmefomCloud.

## Быстрый старт

### 1. Установка

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Создать базу данных PostgreSQL
createdb podmefomcloud

# Миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser
```

### 2. Запуск

```bash
python manage.py runserver
```

Сервер запустится на http://localhost:8000

### 3. Документация API

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/
- OpenAPI JSON: http://localhost:8000/swagger.json

## Структура API

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/register/` | Регистрация |
| POST | `/api/auth/login/` | Вход |
| POST | `/api/auth/refresh/` | Обновить токен |
| POST | `/api/auth/logout/` | Выход |
| GET | `/api/auth/profile/` | Профиль |

### Треки

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/tracks/` | Список одобренных треков |
| POST | `/api/tracks/` | Создать трек |
| GET | `/api/tracks/{id}/` | Детали трека |
| DELETE | `/api/tracks/{id}/` | Удалить трек |
| POST | `/api/tracks/{id}/like/` | Лайкнуть |

### Мои треки

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/my-tracks/` | Все мои треки (включая pending/rejected) |

## Авторизация

API использует JWT токены.

### Получение токенов

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

Ответ:
```json
{
  "access": "eyJ0...",
  "refresh": "eyJ..."
}
```

### Использование токена

```bash
curl http://localhost:8000/api/tracks/ \
  -H "Authorization: Bearer eyJ0..."
```

### Обновление токена

```bash
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ..."}'
```

Ответ (только access):
```json
{
  "access": "eyJ0..."
}
```

## Создание трека

```bash
curl -X POST http://localhost:8000/api/tracks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=My Track" \
  -F "audio=@track.mp3" \
  -F "cover=@cover.jpg" \
  -F "category=track" \
  -F "description=My description"
```

## Модерация

Треки создаются со статусом `pending` и не видны всем до одобрения.

### Админка

- http://localhost:8000/admin/ — основная админка
- **Tracks** — одобренные треки
- **Треки на модерации** — pending треки
- **Отклонённые треки** — rejected треки

## Переменные окружения

Создай `.env` файл:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Требования

- Python 3.10+
- PostgreSQL 14+
- Django 5.x
- See requirements.txt
