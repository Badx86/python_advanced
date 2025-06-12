from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class User(BaseModel):
    """Модель пользователя"""

    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str


class Resource(BaseModel):
    """Модель ресурса"""

    id: int
    name: str
    year: int
    color: str
    pantone_value: str


class Support(BaseModel):
    """Модель блока поддержки"""

    url: str
    text: str


class UsersListResponse(BaseModel):
    """Ответ со списком пользователей"""

    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[User]
    support: Support


class ResourcesListResponse(BaseModel):
    """Ответ со списком ресурсов"""

    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[Resource]
    support: Support


class SingleUserResponse(BaseModel):
    """Ответ с одним пользователем"""

    data: User
    support: Support


class SingleResourceResponse(BaseModel):
    """Ответ с одним ресурсом"""

    data: Resource
    support: Support


# CRUD модели
class CreateUserRequest(BaseModel):
    """Запрос на создание пользователя"""

    name: str
    job: str


class CreateUserResponse(BaseModel):
    """Ответ при создании пользователя"""

    name: str
    job: str
    id: str
    createdAt: datetime


class UpdateUserRequest(BaseModel):
    """Запрос на обновление пользователя"""

    name: Optional[str] = None
    job: Optional[str] = None


class UpdateUserResponse(BaseModel):
    """Ответ при обновлении пользователя"""

    name: Optional[str] = None
    job: Optional[str] = None
    updatedAt: datetime


# Auth модели
class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""

    email: str
    password: str


class RegisterResponse(BaseModel):
    """Ответ при регистрации"""

    id: int
    token: str


class LoginRequest(BaseModel):
    """Запрос на логин"""

    email: str
    password: str


class LoginResponse(BaseModel):
    """Ответ при логине"""

    token: str


class ErrorResponse(BaseModel):
    """Модель ошибки"""

    error: str


# Health Check модель
class AppStatus(BaseModel):
    """Статус приложения"""

    users: bool
    resources: bool
