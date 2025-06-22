"""
Библиотека схем для валидации API ответов с использованием pytest-voluptuous
Централизует все схемы валидации ответов API для удобства поддержки
"""

from pytest_voluptuous import S, Partial
from voluptuous.validators import All, Length, Range, Email, Url, Match
from voluptuous import Required, Any
from typing import Dict, Any as AnyType

# ===================================
# БАЗОВЫЕ СХЕМЫ
# ===================================

# Схема блока поддержки (появляется во многих ответах)
SUPPORT_SCHEMA = Partial({"url": Url(), "text": All(str, Length(min=1))})

# Схема сущности пользователя
USER_SCHEMA = S(
    {
        Required("id"): All(int, Range(min=1)),
        Required("email"): Email(),
        Required("first_name"): All(str, Length(min=1, max=50)),
        Required("last_name"): All(str, Length(min=1, max=50)),
        Required("avatar"): Url(),
    }
)

# Схема сущности ресурса
RESOURCE_SCHEMA = S(
    {
        Required("id"): All(int, Range(min=1)),
        Required("name"): All(str, Length(min=1)),
        Required("year"): Range(min=1900, max=2100),
        Required("color"): Match(r"^#[0-9A-Fa-f]{6}$"),  # hex цвет
        Required("pantone_value"): All(str, Length(min=1)),
    }
)

# Схема пагинации
PAGINATION_SCHEMA = Partial(
    {
        Required("page"): All(int, Range(min=1)),
        Required("size"): All(int, Range(min=1)),
        Required("total"): All(int, Range(min=0)),
        Required("pages"): All(int, Range(min=1)),
    }
)

# ===================================
# СХЕМЫ ОТВЕТОВ API
# ===================================

# Users API
USERS_LIST = S({**PAGINATION_SCHEMA.schema, Required("items"): [USER_SCHEMA]})

SINGLE_USER = S({Required("data"): USER_SCHEMA, Required("support"): SUPPORT_SCHEMA})

USER_CREATED = S(
    {
        Required("name"): str,
        Required("job"): str,
        Required("id"): str,
        Required("createdAt"): Match(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        ),  # ISO datetime
    }
)

USER_UPDATED = S(
    {
        Required("name"): str,
        Required("job"): str,
        Required("updatedAt"): Match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
    }
)

# Resources API
RESOURCES_LIST = S({**PAGINATION_SCHEMA.schema, Required("items"): [RESOURCE_SCHEMA]})

SINGLE_RESOURCE = S(
    {Required("data"): RESOURCE_SCHEMA, Required("support"): SUPPORT_SCHEMA}
)

RESOURCE_CREATED = S(
    {
        Required("name"): str,
        Required("year"): int,
        Required("color"): str,
        Required("pantone_value"): str,
        Required("id"): str,
        Required("createdAt"): Match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
    }
)

RESOURCE_UPDATED = S(
    {
        Required("name"): str,
        Required("year"): int,
        Required("color"): str,
        Required("pantone_value"): str,
        Required("updatedAt"): Match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
    }
)

# Auth API
REGISTER_SUCCESS = S(
    {Required("id"): All(int, Range(min=1)), Required("token"): All(str, Length(min=1))}
)

LOGIN_SUCCESS = S({Required("token"): All(str, Length(min=1))})

# System API
HEALTH_STATUS = S(
    {
        Required("status"): Any("healthy", "unhealthy"),
        Required("timestamp"): Match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*Z"),
        Required("version"): Match(r"\d+\.\d+\.\d+"),
        Required("database"): Partial(
            {
                "status": Any("connected", "disconnected"),
                "type": str,
                "users_count": All(int, Range(min=0)),
            }
        ),
        Required("data"): dict,
        Required("services"): dict,
    }
)

# Схемы ошибок
API_ERROR = S(
    {Required("detail"): Partial({Required("error"): All(str, Length(min=1))})}
)


# ===================================
# РЕЕСТР СХЕМ
# ===================================


class SchemaRegistry:
    """Центральный реестр всех API схем"""

    # Пользователи
    USERS_LIST = USERS_LIST
    SINGLE_USER = SINGLE_USER
    USER_CREATED = USER_CREATED
    USER_UPDATED = USER_UPDATED

    # Ресурсы
    RESOURCES_LIST = RESOURCES_LIST
    SINGLE_RESOURCE = SINGLE_RESOURCE
    RESOURCE_CREATED = RESOURCE_CREATED
    RESOURCE_UPDATED = RESOURCE_UPDATED

    # Аутентификация
    REGISTER_SUCCESS = REGISTER_SUCCESS
    LOGIN_SUCCESS = LOGIN_SUCCESS

    # Система
    HEALTH_STATUS = HEALTH_STATUS

    # Ошибки
    API_ERROR = API_ERROR

    @classmethod
    def validate(cls, schema_name: str, data: Dict[str, AnyType]) -> bool:
        """Утилитарный метод для динамической валидации схем"""
        schema = getattr(cls, schema_name.upper(), None)
        if not schema:
            raise ValueError(f"Schema '{schema_name}' not found")
        return schema == data


# Создаем singleton экземпляр
schemas = SchemaRegistry()
