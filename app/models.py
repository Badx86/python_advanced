from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional, Dict, Any


# ================================
# ТАБЛИЦЫ БАЗЫ ДАННЫХ
# ================================


class User(SQLModel, table=True):
    """Модель пользователя для БД"""

    id: int | None = Field(default=None, primary_key=True)
    email: str
    first_name: str
    last_name: str
    avatar: str


class Resource(SQLModel, table=True):
    """Модель ресурса для БД"""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    year: int
    color: str
    pantone_value: str


# ================================
# МОДЕЛИ ДЛЯ API
# ================================


class Support(SQLModel):
    """Модель блока поддержки"""

    url: str
    text: str


class SingleUserResponse(SQLModel):
    """Ответ с одним пользователем"""

    data: User
    support: Support


class SingleResourceResponse(SQLModel):
    """Ответ с одним ресурсом"""

    data: Resource
    support: Support


class CreateUserRequest(SQLModel):
    """Запрос на создание пользователя"""

    name: str
    job: str


class CreateUserResponse(SQLModel):
    """Ответ при создании пользователя"""

    name: str
    job: str
    id: str
    createdAt: datetime


class UpdateUserRequest(SQLModel):
    """Запрос на обновление пользователя"""

    name: Optional[str] = None
    job: Optional[str] = None


class UpdateUserResponse(SQLModel):
    """Ответ при обновлении пользователя"""

    name: Optional[str] = None
    job: Optional[str] = None
    updatedAt: datetime


# ================================
# СИСТЕМНЫЙ СТАТУС
# ================================


class HealthStatus(SQLModel):
    """Статус здоровья приложения"""

    status: str  # "healthy" | "unhealthy"
    timestamp: str  # ISO timestamp
    version: str  # версия приложения
    database: Dict[
        str, Any
    ]  # {"status": "connected", "type": "postgresql", "users_count": 12}
    data: Dict[
        str, Dict[str, Any]
    ]  # {"users": {"loaded": true, "count": 12}, "resources": {...}}
    services: Dict[str, str]  # {"api": "running", "database": "postgresql"}
