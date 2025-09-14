# ProninTeam
## Описание
Тестовое задание по реализации веб-сервиса на базе Django, предоставляющий CRUD REST API для групповых денежных сборов.
Для просмотра доступных эндпоинтов был добавлен swagger `api/v1/swagger/`

## Приложение API

### Collect - сбор
Модель сбора для проекта.
Доступные операции:
- создание сбора `/api/v1/collects/` (post-запрос)
    Пример запроса:
    ```
    {
    "name": "string",
    "slug": "HjPFTdVmeVSELCLE1_Z_dtkI",
    "event_format": "online",
    "event_reason": "date_birth",
    "event_date": "2025-09-14",
    "event_time": "15:47:29.006Z",
    "event_place": "string",
    "description": "string",
    "min_payment": "-287662.",
    "target_amount": "51544371.",
    "total_amount": "612",
    "logo": "string",
    "stop_date": "2025-09-14T15:47:29.006Z"
    }
    ```
- просмотр сбора `api/v1/collects/{id-сбора}/` (get-запрос)

- редактирование сбора `api/v1/collects/{id-сбора}/` (patch-запрос)
    Допускается редактирование следующих данных: 
    - наименование сбора
    - описание
    - формат события
    - тип события
    - дата события
    Приммер запроса:
    ```
    {
    "name": "string",
    "description": "string",
    "event_format": "online",
    "event_reason": "date_birth",
    "event_date": "2025-09-14"
    }
    ```
- удаление сбора `api/v1/collects/{id-сбора}/` (delete-запрос)
- остановка сбора `api/v1/collects/{id-сбора}/deactivate/` (пустой patch-запрос)
- активация сбора `api/v1/collects/{id-сбора}/activate/` (patch-запрос)
    Для активации сбора допускается:
     - пустой patch запрос
     - patch запрос с одним или двумя параметрами ("new_amount", "new_stop_date")
    Пример запроса:
    ```
    {
    "new_amount": "278",
    "new_stop_date": "2025-09-14T16:01:02"
    }
    ```

### Payment - сбор
Модель платежа для проекта.
Для данной модели доступна одна операция:
- создание платежа `api/v1/collects/{id-сбора}/payments/` (post-запрос)
    Пример запроса:
    ```
    {
    "amount": "1000",
    "hide_amount": true
    }
    ```
Информация о всех созданных платежах размещается в сборе.

### Like - лайк
Модель для лайка платежей
Для данной модели доступны следующие операции:
- создание лайка `api/v1/collects/{id-сбора}/payments/{id-платежа}/like/` (пустой post-запрос)
- удаление лайка `api/v1/collects/{id-сбора}/payments/{id-платежа}/like/delete/` (delete-запрос)
Информация о количестве поставленных на платеж лайках размещается в сборе.

### Comment - комментарий
Модель для комментирования платежей
ля данной модели доступны следующие операции:
- создание комментария `api/v1/collects/{id-сбора}/payments/{id-платежа}/comment/` (post-запрос)
    Пример запроса:
    ```
    {
    "comment": "Hello world!"
    }
    ```
- редактирование комментария `api/v1/collects/{id-сбора}/payments/{id-платежа}/comment/{id-комментария}/` (patch-запрос)
      Пример запроса:
    ```
    {
    "comment": "Hello world! 11"
    }
    ```
- удаление комментария `api/v1/collects/{id-сбора}/payments/{id-платежа}/comment/{id-комментария}/` (delete-запрос)
Информация о количестве комментариев на платеже, а также об их содержимом размещается в сборе.

## Аутентификация и управление пользователями

В приложении используется Djoser для удобного управления пользователями через REST API, а также djangorestframework-simplejwt для токен-базированной аутентификации.

### Основные возможности:

- Регистрация нового пользователя

- Вход пользователя (JWT)

- Выход пользователя (JWT blacklist)

- Сброс и изменение пароля

- Просмотр и обновление профиля

Доступные операции:

- регистрация пользователя `/api/v1/users/` (post-запрос)
    Пример запроса:
		```
        {
        "username": "john",
        "email": "john@example.com",
        "password": "strongpass123"
        }
        ```
Для аутентификации на сайте необходимо отправить post-запрос на адрес `/api/v1/jwt/create/`
    Пример запроса:
    ```
        {
            "username": "string",
            "password": "string"
        }
    ```
    Пример ответа
    ```
    {
        "refresh": "example",
        "access": "example"
    }
    ```
В дальнейшем при каждом запросе к API нужно в заголовке запроса, в поле Authorization, передавать основной токен доступа, полученный в поле access. Перед самим токеном должно стоять ключевое слово Bearer и пробел: Bearer token

- получение информации о текущем пользователе `/api/v1/users/me/` (get-запрос)
    Пример запроса:
    Authorization: Bearer <access_token>
- редактирование пользователя `/api/v1/users/me/` (patch-запрос)
    Пример запроса:
    ```
    {
    "email": "user@example.com"
    }
    ```
- удаление пользователя `/api/v1/users/me/` (delete-запрос)

- изменение пароля для авторизованного пользователя `/api/v1/users/set_password/`
    Пример запроса:
    ```
    {
    "new_password": "newpass123",
    "current_password": "oldpass123"
    }
    ```

## Инструкция по локальному запуску проекта на вашем рабочем месте:

### Установка и локальный запуск проекта:

1. Клонируйте репозиторий через Git
cd <ваша директория, в которую вы хотите разместить проект>
git clone <SSH-ключ данного репозитория>
2. Создайте виртуальное окружение и активируйте его
**Windows**
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```
**Linux/macOS**
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
3. Установите зависимости
```bash
pip install -r backend/requirements.txt
```
4. Скачайте и установите Docker Desktop с официального сайта: https://www.docker.com
   
5. Для локального запуска проекта необходимо выполнить следующие команды:
```bash
- docker-compose up -d --build
- docker compose exec backend python manage.py makemigrations api || echo "No new migrations"
- docker compose exec backend python manage.py migrate
- docker compose exec backend python manage.py createsuperuser
```

6. Добавление тестовых данных:
```bash
docker compose exec backend python manage.py populate_db --users 100 --collects 50 --payments 1000 --comments 2000 --likes 1500
 docker compose exec backend python manage.py update_collects
```

7. Пример заполнения .env файла:
```bash
DEBUG=True
SECRET_KEY="django-insecure-6an+c-*%f&e!c+9cxg&2x%d5!_msnbj&@z(1zdlq-cfs7tco1^"


CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_RESULT_BACKEND="redis://redis:6379/0"
CELERY_ACCEPT_CONTENT='["json"]'
CELERY_TASK_SERIALIZER="json"
CELERY_RESULT_SERIALIZER="json"

EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST="smtp.mail.ru"
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER="your_email@mail.ru"
EMAIL_HOST_PASSWORD="your_password"
DEFAULT_FROM_EMAIL="no-reply@example.com"


POSTGRES_DB=proninteam_db
POSTGRES_USER=proninteam_user
POSTGRES_PASSWORD=proninteam_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

Форматирование кода
```bash
black {source_file_or_directory}
```

1. Сайт будет доступен в браузере по следующей ссылке http://127.0.0.1:8000/.


