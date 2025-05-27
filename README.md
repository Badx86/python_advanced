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

### Список пользователей

```
GET /api/users?page=1&per_page=6
```

### Один пользователь

```
GET /api/users/2    # Существующий
GET /api/users/999  # 404 Not Found
```

## Файлы

- `main.py` - FastAPI сервер
- `tests/test_reqres.py` - Тесты с Pydantic валидацией
- `app/models.py` - Pydantic модели для валидации
- `tests/conftest.py` - Pytest фикстуры
- `requirements.txt` - Зависимости

## Тесты

Покрыто тестами:

- ✅ Список пользователей (пагинация)
- ✅ Получение пользователя по ID
- ✅ 404 для несуществующих пользователей

Заготовки для будущего (не покрыто тестами):

- ❌ Ресурсы
- ❌ CRUD операции
- ❌ Аутентификация