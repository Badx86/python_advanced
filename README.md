# FastAPI Reqres with PostgreSQL

Микросервис на FastAPI с автотестами и **интеграцией PostgreSQL**.

## Основные возможности

- **PostgreSQL интеграция** - пользователи хранятся в базе данных
- **Docker Compose** - полная инфраструктура (API + PostgreSQL + Adminer)  
- **Автоматическая миграция** - создание таблиц и загрузка данных при старте
- **Расширенный healthcheck** - подробная информация о состоянии системы
- **CRUD тесты с реальной БД** - изолированное тестирование операций
- **SQLModel ORM** - современный подход к работе с базой данных
- **Пагинация** - эффективная обработка больших наборов данных
- **Подробное логирование** - логи всех операций

## Установка и запуск

### 🐳 1. Через Docker (рекомендуется)

```bash
# Клонировать репозиторий
git clone <repo-url>
cd python_advanced

# Запустить всю инфраструктуру
docker-compose up --build

# Сервер будет доступен на:
# - API: http://localhost:8000
# - PostgreSQL: localhost:5432
# - Adminer (веб-интерфейс БД): http://localhost:8080
```

**Что включено в Docker Compose:**
- **FastAPI app** - основное приложение на порту 8000
- **PostgreSQL 15** - база данных на порту 5432
- **Adminer** - веб-интерфейс для управления БД на порту 8080

### 🔧 2. Локальная разработка

```bash
# Установка Poetry (если еще не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Установка зависимостей проекта
poetry install

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл
```

## Настройка окружения

Создайте `.env` файл в корне проекта:

| Переменная | Описание | Значение по умолчанию | Обязательно |
|------------|----------|----------------------|-------------|
| DATABASE_ENGINE | Строка подключения к PostgreSQL | - | Да |
| DATABASE_POOL_SIZE | Размер пула соединений | 10 | Нет |
| HOST | IP адрес для запуска сервера | 0.0.0.0 | Нет |
| PORT | Порт для запуска сервера | 8000 | Нет |
| API_URL | Базовый URL для тестов | http://localhost:8000 | Да |
| APP_VERSION | Версия приложения | 1.0.0 | Нет |

Пример `.env`:

```bash
DATABASE_ENGINE=postgresql+psycopg2://postgres:example@localhost:5432/postgres
DATABASE_POOL_SIZE=10
HOST=0.0.0.0
PORT=8000
API_URL=http://localhost:8000
APP_VERSION=1.0.0
```

### 🚀 3. Запуск локально

```bash
# Запустить PostgreSQL (через Docker)
docker-compose up db -d

# Запустить приложение
poetry run python app/main.py

# Сервер: http://localhost:8000
```

### 4. Запуск тестов

```bash
# Все тесты (убедитесь что сервер запущен)
poetry run pytest tests/ -v

# По маркерам
poetry run pytest -m smoke          # Smoke тесты
poetry run pytest -m auth           # Аутентификация  
poetry run pytest -m crud           # CRUD операции
poetry run pytest -m pagination     # Пагинация
poetry run pytest -m "not slow"     # Исключить медленные

# Конкретный файл
poetry run pytest tests/test_auth.py -v

# С покрытием
poetry run pytest --cov=app tests/
```

## 🗄️ База данных

### Подключение к PostgreSQL

**Через Docker (Adminer):**
- URL: http://localhost:8080
- Система: PostgreSQL
- Сервер: db
- Пользователь: postgres
- Пароль: example
- База данных: postgres

**Через CLI:**
```bash
# Подключение к контейнеру PostgreSQL
docker exec -it fastapi_postgres psql -U postgres -d postgres

# Или через локальный клиент
psql -h localhost -U postgres -d postgres
```

### Данные

При первом запуске приложение автоматически:
1. Создает таблицы в PostgreSQL (User, Resource)
2. Загружает 12 тестовых пользователей из `app/data/users.json` в базу данных
3. Ресурсы на данный момент читаются из `app/data/resources.json` (без БД)

## API

Сервер автоматически генерирует интерактивную документацию:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Основные эндпоинты:

**Система:**
- `GET /status` - Подробный статус приложения с информацией о БД

**Пользователи:**
- `GET /api/users` - Список пользователей (с пагинацией и delay)
- `GET /api/users/{id}` - Получить пользователя по ID
- `POST /api/users` - Создать пользователя (сохраняется в БД)
- `PUT /api/users/{id}` - Полное обновление пользователя
- `PATCH /api/users/{id}` - Частичное обновление пользователя
- `DELETE /api/users/{id}` - Удалить пользователя (из БД)

**Аутентификация:**
- `POST /api/register` - Регистрация (с валидацией email)
- `POST /api/login` - Вход в систему

**Ресурсы:**
- `GET /api/unknown` - Список ресурсов (из JSON файла)
- `GET /api/unknown/{id}` - Получить ресурс по ID

## Структура проекта

```
├── app/
│   ├── data/
│   │   ├── users.json           # Тестовые данные пользователей (seed)
│   │   └── resources.json       # Тестовые данные ресурсов
│   ├── database/
│   │   ├── engine.py            # Настройка SQLModel и PostgreSQL
│   │   ├── seed.py              # Загрузка seed данных в БД
│   │   └── users.py             # CRUD операции для пользователей
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Эндпоинты аутентификации
│   │   ├── resources.py         # Эндпоинты ресурсов
│   │   ├── system.py            # Системные эндпоинты (healthcheck)
│   │   └── users.py             # Эндпоинты пользователей
│   ├── main.py                  # FastAPI приложение и настройка
│   └── models.py                # SQLModel модели для БД и API
├── tests/
│   ├── test_auth.py             # Тесты аутентификации (email валидация)
│   ├── test_crud.py             # CRUD операции с реальной БД
│   ├── test_resources.py        # Тесты ресурсов
│   ├── test_smoke.py            # Smoke тесты
│   ├── test_special.py          # Специальные тесты (delayed response)
│   ├── test_users.py            # Тесты пользователей
│   ├── conftest.py              # Pytest фикстуры и API клиент
│   └── assertions.py            # Хелперы для проверок в тестах
├── docker-compose.yml           # Docker инфраструктура
├── Dockerfile                   # Образ FastAPI приложения
├── pyproject.toml               # Poetry конфигурация и зависимости
├── poetry.lock                  # Закрепленные версии зависимостей
├── .env                         # Переменные окружения
├── .gitignore                   # Git ignore файл
├── api.log                      # Логи API (генерируется автоматически)
└── README.md                    # Документация проекта
```

## Тесты

**Всего: ~40 тестов** разбитых по функциональным областям.

### Покрытие:

- **Smoke тесты** - доступность сервиса, статус приложения
- **Аутентификация** - регистрация/логин с email валидацией  
- **CRUD операции** - создание/обновление/удаление пользователей в БД
- **Пользователи** - получение, пагинация, уникальность ID
- **Ресурсы** - получение, пагинация ресурсов (из JSON)
- **Специальные** - delayed response с измерением времени

### Особенности тестирования:

- **Изоляция тестов** - каждый тест работает независимо
- **Реальная БД** - CRUD тесты создают/удаляют записи в PostgreSQL
- **Автоматическая проверка** доступности сервиса перед запуском
- **Параметризованные тесты** для покрытия различных сценариев
- **Подробные логи** всех операций для отладки

## 🔧 Разработка

### Полезные команды:

```bash
# Перезапуск только приложения (без БД)
docker-compose up app --build

# Просмотр логов
docker-compose logs app
docker-compose logs db

# Остановка всех сервисов
docker-compose down

# Очистка данных БД
docker-compose down -v

# Форматирование кода
poetry run black app/ tests/

# Линтинг
poetry run pylint app/

# Просмотр зависимостей
poetry show --tree
```

### Мониторинг:

```bash
# Проверка статуса приложения
curl http://localhost:8000/status

# Проверка здоровья PostgreSQL
docker-compose exec db pg_isready -U postgres

# Просмотр статистики Docker
docker stats
```

## Особенности

- **Модульная архитектура** - роуты разделены по функциональным областям
- **SQLModel интеграция** - современный ORM от создателя FastAPI
- **Connection pooling** - эффективное управление соединениями с БД
- **Автоматические миграции** - создание таблиц при старте приложения  
- **Автозагрузка данных** - seed данные загружаются при первом запуске
- **Email валидация** с использованием `email-validator`
- **Delayed response** для тестирования с задержкой
- **Health check** с проверкой состояния БД
- **Docker** - контейнеризация
- **Adminer интеграция** - веб-интерфейс для управления БД

## 🐛 Отладка

### Распространенные проблемы:

**База данных недоступна:**
```bash
# Проверить статус контейнеров
docker-compose ps

# Перезапустить БД
docker-compose restart db

# Проверить логи БД
docker-compose logs db
```

**Ошибки в тестах:**
```bash
# Убедиться что сервер запущен
curl http://localhost:8000/status

# Проверить переменные окружения
cat .env

# Запустить конкретный тест с подробными логами
poetry run pytest tests/test_smoke.py::TestSmoke::test_service_is_alive -v -s
```

**Проблемы с зависимостями:**
```bash
# Переустановить зависимости
poetry install --no-cache

# Обновить lock файл
poetry lock --no-update
```