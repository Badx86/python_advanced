from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import HttpUrl, BaseModel


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
# МОДЕЛИ ДЛЯ API ЗАПРОСОВ
# ================================


class UserCreate(SQLModel):
    """Создание пользователя"""

    name: str
    job: str


class UserUpdate(SQLModel):
    """Обновление пользователя"""

    name: Optional[str] = None
    job: Optional[str] = None


class RegisterRequest(SQLModel):
    """Запрос регистрации"""

    email: str
    password: str


class LoginRequest(SQLModel):
    """Запрос входа"""

    email: str
    password: str


class ResourceCreate(SQLModel):
    """Создание ресурса"""

    name: str
    year: int
    color: str
    pantone_value: str


class ResourceUpdate(SQLModel):
    """Обновление ресурса"""

    name: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    pantone_value: Optional[str] = None


# ================================
# МОДЕЛИ ДЛЯ API ОТВЕТОВ
# ================================


class Support(SQLModel):
    """Модель блока поддержки"""

    url: HttpUrl
    text: str


class RegisterResponse(SQLModel):
    """Ответ регистрации"""

    id: int
    token: str


class LoginResponse(SQLModel):
    """Ответ входа"""

    token: str


class UserResponse(BaseModel):
    """Универсальный ответ для создания/обновления пользователя"""

    name: Optional[str] = None
    job: Optional[str] = None
    id: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class ResourceResponse(BaseModel):
    """Универсальный ответ для создания/обновления ресурса"""

    name: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    pantone_value: Optional[str] = None
    id: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class SingleUserResponse(SQLModel):
    """Ответ с одним пользователем (с support блоком)"""

    data: User
    support: Support


class SingleResourceResponse(SQLModel):
    """Ответ с одним ресурсом (с support блоком)"""

    data: Resource
    support: Support


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
