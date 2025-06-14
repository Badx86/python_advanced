import json
import logging
import random
import time
from datetime import datetime
from http import HTTPStatus
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from fastapi_pagination import Page
from app.models import (
    CreateUserRequest,
    CreateUserResponse,
    UpdateUserRequest,
    UpdateUserResponse,
    User,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Загружаем пользователей из JSON
with open("app/data/users.json", "r", encoding="utf-8") as f:
    users_json = json.load(f)
    users_data = [User(**user) for user in users_json]


def paginate_data(data, page: int, size: int) -> Page:
    """Универсальная функция пагинации"""
    total = len(data)
    start_index = (page - 1) * size
    end_index = start_index + size
    items = data[start_index:end_index]
    total_pages = (total + size - 1) // size

    return Page(items=items, page=page, size=size, total=total, pages=total_pages)


def find_user_by_id(user_id: int) -> User | None:
    """Поиск пользователя по ID"""
    return next((user for user in users_data if user.id == user_id), None)


@router.get("/api/users", tags=["Users"])
def get_users_with_delay(
    page: int = Query(1, ge=1),
    size: int = Query(6, ge=1, le=50, alias="per_page"),
    delay: int = Query(0, ge=0, le=10),
) -> Page[User]:
    """Получить список пользователей с пагинацией и опциональной задержкой"""
    logger.info(f"Getting users list: page={page}, per_page={size}, delay={delay}")

    # Добавляем задержку если указана
    if delay > 0:
        logger.info(f"Applying delay: {delay} seconds")
        time.sleep(delay)

    users_page = paginate_data(users_data, page, size)
    logger.info(f"Returning {len(users_page.items)} users for page {page}")
    return users_page


@router.get("/api/users/{user_id}", tags=["Users"])
def get_single_user(user_id: int) -> Dict[str, Any]:
    """Получить пользователя по ID"""
    logger.info(f"Getting single user: user_id={user_id}")
    user = find_user_by_id(user_id)
    if not user:
        logger.warning(f"User {user_id} not found")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"User {user_id} not found"},
        )

    logger.info(f"Found user: {user.first_name} {user.last_name}")
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
    logger.info(f"Creating user: name={user_data.name}, job={user_data.job}")
    new_id = str(random.randint(100, 9999))
    created_at = datetime.now()
    logger.info(f"Created user with ID: {new_id}")
    return CreateUserResponse(
        name=user_data.name, job=user_data.job, id=new_id, createdAt=created_at
    )


@router.put("/api/users/{user_id}", tags=["Users"])
def update_user_put(user_id: int, user_data: UpdateUserRequest) -> UpdateUserResponse:
    """Полное обновление пользователя"""
    logger.info(
        f"PUT updating user {user_id}: name={user_data.name}, job={user_data.job}"
    )
    updated_at = datetime.now()
    logger.info(f"Updated user {user_id}")
    return UpdateUserResponse(
        name=user_data.name, job=user_data.job, updatedAt=updated_at
    )


@router.patch("/api/users/{user_id}", tags=["Users"])
def update_user_patch(user_id: int, user_data: UpdateUserRequest) -> UpdateUserResponse:
    """Частичное обновление пользователя"""
    logger.info(
        f"PATCH updating user {user_id}: name={user_data.name}, job={user_data.job}"
    )
    updated_at = datetime.now()
    logger.info(f"Patched user {user_id}")
    return UpdateUserResponse(
        name=user_data.name, job=user_data.job, updatedAt=updated_at
    )


@router.delete(
    "/api/users/{user_id}", status_code=HTTPStatus.NO_CONTENT, tags=["Users"]
)
def delete_user(user_id: int) -> None:
    """Удалить пользователя"""
    logger.info(f"Deleting user {user_id}")
