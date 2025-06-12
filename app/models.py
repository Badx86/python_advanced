from pydantic import BaseModel
from datetime import datetime
from typing import Optional


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


class SingleUserResponse(BaseModel):
    """Ответ с одним пользователем"""

    data: User
    support: Support


class SingleResourceResponse(BaseModel):
    """Ответ с одним ресурсом"""

    data: Resource
    support: Support


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


class AppStatus(BaseModel):
    """Статус приложения"""

    users: bool
    resources: bool
