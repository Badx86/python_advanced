from app.exceptions import UserNotFoundError, ValidationError, InvalidIDError
from fastapi import APIRouter, HTTPException, Query
from app.database.users import get_users_paginated
from fastapi_pagination import Params, Page
from app.database.engine import engine
from app.models import User
from datetime import datetime
from http import HTTPStatus
from typing import Dict, Any
from fastapi import Depends
from sqlmodel import Session
import logging
import random
import time
from app.models import (
    CreateUserRequest,
    CreateUserResponse,
    UpdateUserRequest,
    UpdateUserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/users", tags=["Users"])
def get_users_with_delay(
    params: Params = Depends(),
    delay: int = Query(0, ge=0, le=10),
) -> Page[User]:
    """Получить список пользователей с пагинацией и опциональной задержкой"""

    # Добавляем задержку если указана
    if delay > 0:
        time.sleep(delay)

    # Создаем session и передаем в database функцию
    with Session(engine) as session:
        users_page = get_users_paginated(session)

    return users_page


@router.get("/api/users/{user_id}", tags=["Users"])
def get_single_user(user_id: int) -> Dict[str, Any]:
    """Получить пользователя по ID"""

    # Валидация ID
    if user_id < 1:
        raise InvalidIDError("user ID")

    from app.database.users import get_user

    # Получаем пользователя из БД
    user = get_user(user_id)
    if not user:
        raise UserNotFoundError(user_id)

    return {
        "data": user.model_dump(),
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


@router.post("/api/users", status_code=201, tags=["Users"])
def create_user(user_data: CreateUserRequest) -> CreateUserResponse:
    """Создать нового пользователя"""

    # Валидация данных
    if not user_data.name or not user_data.name.strip():
        raise ValidationError("Name is required")
    if not user_data.job or not user_data.job.strip():
        raise ValidationError("Job is required")

    # Генерируем email и avatar для совместимости с моделью User
    generated_email = f"{user_data.name.lower().replace(' ', '.')}@example.com"
    generated_avatar = f"https://reqres.in/img/faces/{random.randint(1, 12)}-image.jpg"

    from app.database.users import create_user as db_create_user

    try:
        # Сохраняем в БД
        db_user = db_create_user(
            email=generated_email,
            first_name=(
                user_data.name.split()[0] if user_data.name.split() else user_data.name
            ),
            last_name=(
                user_data.name.split()[-1] if len(user_data.name.split()) > 1 else ""
            ),
            avatar=generated_avatar,
        )

        if not db_user:
            raise ValidationError("Failed to create user")

        # Возвращаем ответ в формате API (с реальным ID из БД)
        created_at = datetime.now()
        return CreateUserResponse(
            name=user_data.name,
            job=user_data.job,
            id=str(db_user.id),
            createdAt=created_at,
        )

    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise ValidationError("Failed to create user")


@router.put("/api/users/{user_id}", tags=["Users"])
def update_user_put(user_id: int, user_data: UpdateUserRequest) -> UpdateUserResponse:
    """Полное обновление пользователя"""

    # Валидация ID
    if user_id < 1:
        raise InvalidIDError("user ID")

    # Проверяем существование пользователя
    from app.database.users import get_user, update_user as db_update_user

    existing_user = get_user(user_id)
    if not existing_user:
        raise UserNotFoundError(user_id)

    try:
        # Обновляем пользователя в БД
        if user_data.name:
            name_parts = user_data.name.split()
            first_name = name_parts[0] if name_parts else user_data.name
            last_name = name_parts[-1] if len(name_parts) > 1 else ""

            db_update_user(user_id=user_id, first_name=first_name, last_name=last_name)

        updated_at = datetime.now()
        return UpdateUserResponse(
            name=user_data.name, job=user_data.job, updatedAt=updated_at
        )

    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        raise ValidationError("Failed to update user")


@router.patch("/api/users/{user_id}", tags=["Users"])
def update_user_patch(user_id: int, user_data: UpdateUserRequest) -> UpdateUserResponse:
    """Частичное обновление пользователя"""

    # Валидация ID
    if user_id < 1:
        raise InvalidIDError("user ID")

    # Проверяем существование пользователя
    from app.database.users import get_user, update_user as db_update_user

    existing_user = get_user(user_id)
    if not existing_user:
        raise UserNotFoundError(user_id)

    try:
        # Частичное обновление в БД
        if user_data.name:
            name_parts = user_data.name.split()
            first_name = name_parts[0] if name_parts else user_data.name
            last_name = name_parts[-1] if len(name_parts) > 1 else ""

            db_update_user(user_id=user_id, first_name=first_name, last_name=last_name)

        updated_at = datetime.now()
        return UpdateUserResponse(
            name=user_data.name, job=user_data.job, updatedAt=updated_at
        )

    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        raise ValidationError("Failed to update user")


@router.delete("/api/users/{user_id}", status_code=204, tags=["Users"])
def delete_user(user_id: int) -> None:
    """Удалить пользователя"""

    # Валидация ID
    if user_id < 1:
        raise InvalidIDError("user ID")

    from app.database.users import delete_user as db_delete_user

    try:
        # Удаляем из БД
        deleted = db_delete_user(user_id)

        # Корректное поведение - 404 если пользователя не было
        if not deleted:
            raise UserNotFoundError(user_id)

    except UserNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        raise ValidationError("Failed to delete user")
