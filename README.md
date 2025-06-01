# FastAPI Reqres

Микросервис на FastAPI с автотестами.

## Запуск

### 1. Установка

```bash
pip install -r requirements.txt
```

### 2. Запуск сервера

```bash
python main.py
```

Сервер: http://localhost:8000

### 3. Запуск тестов

```bash
pytest test_reqres.py -v
```

## API

### Пользователи

```
GET /api/users?page=1&per_page=6     # Список пользователей
GET /api/users/2                     # Один пользователь
GET /api/users/999                   # 404 Not Found
POST /api/users                      # Создание пользователя  
PUT /api/users/2                     # Полное обновление
PATCH /api/users/2                   # Частичное обновление
DELETE /api/users/2                  # Удаление (204)
```

### Ресурсы

```
GET /api/unknown                     # Список ресурсов
GET /api/unknown/2                   # Один ресурс
GET /api/unknown/23                  # 404 Not Found
```

## Файлы

- `app/main.py` - FastAPI сервер
- `app/models.py` - Pydantic модели для валидации
- `tests/test_reqres.py` - Тесты с Pydantic валидацией
- `tests/conftest.py` - Pytest фикстуры
- `tests/assertions.py` - Хелперы для проверок в тестах
- `requirements.txt` - Зависимости

## Тесты

Покрыто тестами:

**Пользователи:**

- ✅ Список пользователей (пагинация)
- ✅ Получение пользователя по ID
- ✅ 404 для несуществующих пользователей
- ✅ Создание пользователя (POST)
- ✅ Обновление пользователя (PUT/PATCH)
- ✅ Удаление пользователя (DELETE)

**Ресурсы:**

- ✅ Список ресурсов (пагинация)
- ✅ Получение ресурса по ID
- ✅ 404 для несуществующих ресурсов

Заготовки для будущего (не покрыто тестами):

- ❌ Аутентификация
- ❌ Задержанные ответы

## Особенности

- Тестовые данные генерируются с помощью `mimesis`
- Универсальные хелперы для проверок в `assertions.py`
- Структура файлов разделена на `app/` и `tests/`