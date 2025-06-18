import logging
import random
import time
from datetime import datetime
from http import HTTPStatus
from typing import Dict, Any
from fastapi import Depends
from fastapi_pagination import Params, Page
from app.models import User
from fastapi import APIRouter, HTTPException, Query
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
    logger.info(
        f"[API] Getting users list: page={params.page}, size={params.size}, delay={delay}"
    )

    # Добавляем задержку если указана
    if delay > 0:
        logger.info(f"[API] Applying delay: {delay} seconds")
        time.sleep(delay)

    from app.database.users import get_users_paginated

    # Получаем пользователей из БД с пагинацией
    users_page = get_users_paginated(page=params.page, size=params.size)
    logger.info(f"[API] Returning {len(users_page.items)} users for page {params.page}")
    return users_page


@router.get("/api/users/{user_id}", tags=["Users"])
def get_single_user(user_id: int) -> Dict[str, Any]:
    """Получить пользователя по ID"""
    logger.info(f"[API] Getting single user: user_id={user_id}")

    # Валидация ID
    if user_id < 1:
        logger.warning(f"[API] Invalid user ID: {user_id}")
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID"
        )

    from app.database.users import get_user

    # Получаем пользователя из БД
    user = get_user(user_id)
    if not user:
        logger.warning(f"[API] User {user_id} not found")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"User {user_id} not found"},
        )

    logger.info(f"[API] Found user: {user.first_name} {user.last_name}")
    return {
        "data": user.model_dump(),
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


@router.post("/api/users", status_code=HTTPStatus.CREATED, tags=["Users"])
def create_user(user_data: CreateUserRequest) -> CreateUserResponse:
    """Создать нового пользователя"""
    logger.info(f"[API] Creating user: name={user_data.name}, job={user_data.job}")

    # Валидация данных
    if not user_data.name or not user_data.name.strip():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Name is required"
        )
    if not user_data.job or not user_data.job.strip():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Job is required"
        )

    # Генерируем email и avatar для совместимости с моделью User
    generated_email = f"{user_data.name.lower().replace(' ', '.')}@example.com"
    generated_avatar = f"https://reqres.in/img/faces/{random.randint(1, 12)}-image.jpg"

    from app.database.users import create_user as db_create_user

    # Сохраняем в БД
    db_user = db_create_user(
        email=generated_email,
        first_name=(
            user_data.name.split()[0] if user_data.name.split() else user_data.name
        ),
        last_name=user_data.name.split()[-1] if len(user_data.name.split()) > 1 else "",
        avatar=generated_avatar,
    )

    if not db_user:
        logger.error(f"[API] Failed to create user in database")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to create user"
        )

    # Возвращаем ответ в формате API (с реальным ID из БД)
    created_at = datetime.now()
    logger.info(f"[API] Created user with ID: {db_user.id}")
    return CreateUserResponse(
        name=user_data.name,
        job=user_data.job,
        id=str(db_user.id),
        createdAt=created_at,
    )


@router.put("/api/users/{user_id}", tags=["Users"])
def update_user_put(user_id: int, user_data: UpdateUserRequest) -> UpdateUserResponse:
    """Полное обновление пользователя"""
    logger.info(
        f"[API] PUT updating user {user_id}: name={user_data.name}, job={user_data.job}"
    )

    # Валидация ID
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID"
        )

    # Проверяем существование пользователя
    from app.database.users import get_user, update_user as db_update_user

    existing_user = get_user(user_id)
    if not existing_user:
        logger.warning(f"[API] User {user_id} not found for update")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"User {user_id} not found"},
        )

    # Обновляем пользователя в БД
    if user_data.name:
        name_parts = user_data.name.split()
        first_name = name_parts[0] if name_parts else user_data.name
        last_name = name_parts[-1] if len(name_parts) > 1 else ""

        db_update_user(user_id=user_id, first_name=first_name, last_name=last_name)

    updated_at = datetime.now()
    logger.info(f"[API] Updated user {user_id}")
    return UpdateUserResponse(
        name=user_data.name, job=user_data.job, updatedAt=updated_at
    )


@router.patch("/api/users/{user_id}", tags=["Users"])
def update_user_patch(user_id: int, user_data: UpdateUserRequest) -> UpdateUserResponse:
    """Частичное обновление пользователя"""
    logger.info(
        f"[API] PATCH updating user {user_id}: name={user_data.name}, job={user_data.job}"
    )

    # Валидация ID
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID"
        )

    # Проверяем существование пользователя
    from app.database.users import get_user, update_user as db_update_user

    existing_user = get_user(user_id)
    if not existing_user:
        logger.warning(f"[API] User {user_id} not found for update")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"User {user_id} not found"},
        )

    # Частичное обновление в БД
    if user_data.name:
        name_parts = user_data.name.split()
        first_name = name_parts[0] if name_parts else user_data.name
        last_name = name_parts[-1] if len(name_parts) > 1 else ""

        db_update_user(user_id=user_id, first_name=first_name, last_name=last_name)

    updated_at = datetime.now()
    logger.info(f"[API] Patched user {user_id}")
    return UpdateUserResponse(
        name=user_data.name, job=user_data.job, updatedAt=updated_at
    )


@router.delete(
    "/api/users/{user_id}", status_code=HTTPStatus.NO_CONTENT, tags=["Users"]
)
def delete_user(user_id: int) -> None:
    """Удалить пользователя"""
    logger.info(f"[API] Deleting user {user_id}")

    # Валидация ID
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid user ID"
        )

    from app.database.users import delete_user as db_delete_user

    # Удаляем из БД
    deleted = db_delete_user(user_id)

    # Корректное поведение - 404 если пользователя не было
    if not deleted:
        logger.warning(f"[API] User {user_id} not found for deletion")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"User {user_id} not found"},
        )

    logger.info(f"[API] User {user_id} deleted successfully")
