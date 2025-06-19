from fastapi import APIRouter, Query, Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import Session, select
from datetime import datetime
import logging
import random
import time

from app.database.engine import engine
from app.models import (
    User,
    UserCreate,
    UserUpdate,
    UserResponse,
    SingleUserResponse,
    Support,
)
from app.exceptions import UserNotFoundError, ValidationError, InvalidIDError

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

    # Работаем напрямую с БД
    with Session(engine) as session:
        query = select(User).order_by(User.id)
        return paginate(session, query, params)


@router.get("/api/users/{user_id}", tags=["Users"])
def get_single_user(user_id: int) -> SingleUserResponse:
    """Получить пользователя по ID"""

    # Валидация ID
    if user_id < 1:
        raise InvalidIDError("user ID")

    # Получаем пользователя из БД
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise UserNotFoundError(user_id)

    return SingleUserResponse(
        data=user,
        support=Support(
            url="https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            text="Tired of writing endless social media content? Let Content Caddy generate it for you.",
        ),
    )


@router.post("/api/users", status_code=201, tags=["Users"])
def create_user(user_data: UserCreate) -> UserResponse:
    """Создать нового пользователя"""

    # Валидация данных
    if not user_data.name or not user_data.name.strip():
        raise ValidationError("Name is required")
    if not user_data.job or not user_data.job.strip():
        raise ValidationError("Job is required")

    # Генерируем email и avatar для совместимости с моделью User
    generated_email = f"{user_data.name.lower().replace(' ', '.')}@example.com"
    generated_avatar = f"https://reqres.in/img/faces/{random.randint(1, 12)}-image.jpg"

    try:
        # Сохраняем в БД напрямую
        with Session(engine) as session:
            # Парсим имя
            name_parts = user_data.name.split()
            first_name = name_parts[0] if name_parts else user_data.name
            last_name = name_parts[-1] if len(name_parts) > 1 else ""

            db_user = User(
                email=generated_email,
                first_name=first_name,
                last_name=last_name,
                avatar=generated_avatar,
            )

            session.add(db_user)
            session.commit()
            session.refresh(db_user)

        # Возвращаем ответ в формате API
        return UserResponse(
            name=user_data.name,
            job=user_data.job,
            id=str(db_user.id),
            createdAt=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise ValidationError("Failed to create user")


@router.put("/api/users/{user_id}", tags=["Users"])
def update_user_put(user_id: int, user_data: UserUpdate) -> UserResponse:
    """Полное обновление пользователя"""

    # Валидация ID
    if user_id < 1:
        raise InvalidIDError("user ID")

    try:
        with Session(engine) as session:
            # Проверяем существование пользователя
            user = session.get(User, user_id)
            if not user:
                raise UserNotFoundError(user_id)

            # Обновляем пользователя в БД
            if user_data.name:
                name_parts = user_data.name.split()
                user.first_name = name_parts[0] if name_parts else user_data.name
                user.last_name = name_parts[-1] if len(name_parts) > 1 else ""

            session.add(user)
            session.commit()
            session.refresh(user)

        return UserResponse(
            name=user_data.name,
            job=user_data.job,
            id=str(user.id),
            updatedAt=datetime.now(),
        )

    except UserNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        raise ValidationError("Failed to update user")


@router.patch("/api/users/{user_id}", tags=["Users"])
def update_user_patch(user_id: int, user_data: UserUpdate) -> UserResponse:
    """Частичное обновление пользователя"""

    # Валидация ID
    if user_id < 1:
        raise InvalidIDError("user ID")

    try:
        with Session(engine) as session:
            # Проверяем существование пользователя
            user = session.get(User, user_id)
            if not user:
                raise UserNotFoundError(user_id)

            # Частичное обновление в БД
            if user_data.name:
                name_parts = user_data.name.split()
                user.first_name = name_parts[0] if name_parts else user_data.name
                user.last_name = name_parts[-1] if len(name_parts) > 1 else ""

            session.add(user)
            session.commit()
            session.refresh(user)

        return UserResponse(
            name=user_data.name,
            job=user_data.job,
            id=str(user.id),
            updatedAt=datetime.now(),
        )

    except UserNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        raise ValidationError("Failed to update user")


@router.delete("/api/users/{user_id}", status_code=204, tags=["Users"])
def delete_user(user_id: int) -> None:
    """Удалить пользователя"""

    # Валидация ID
    if user_id < 1:
        raise InvalidIDError("user ID")

    try:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user:
                raise UserNotFoundError(user_id)

            session.delete(user)
            session.commit()

    except UserNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        raise ValidationError("Failed to delete user")
