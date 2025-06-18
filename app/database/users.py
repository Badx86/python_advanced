from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Iterable, Optional
from sqlmodel import Session, select, func
from fastapi_pagination import Page, Params
from app.database.engine import engine
from app.models import User
import logging

logger = logging.getLogger(__name__)


def get_user(user_id: int) -> Optional[User]:
    """Поиск пользователя по ID"""
    try:
        with Session(engine) as session:
            user = session.get(User, user_id)
            return user
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None


def get_users_paginated(session: Session) -> Page[User]:
    """Получить список пользователей с пагинацией"""
    try:
        query = select(User).order_by(User.id)
        result = paginate(session, query)
        return result

    except Exception as e:
        logger.error(f"Error getting users: {e}")
        # В случае ошибки возвращаем пустую страницу
        return Page(items=[], page=1, size=6, total=0, pages=0)


def get_all_users() -> Iterable[User]:
    """Получить всех пользователей (для системных нужд)"""
    try:
        with Session(engine) as session:
            statement = select(User)
            users = session.exec(statement).all()
            return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []


def create_user(
    email: str, first_name: str, last_name: str, avatar: str = ""
) -> Optional[User]:
    """Создать нового пользователя в БД"""
    try:
        with Session(engine) as session:
            new_user = User(
                email=email, first_name=first_name, last_name=last_name, avatar=avatar
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None


def update_user(
    user_id: int,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    avatar: Optional[str] = None,
) -> Optional[User]:
    """Обновить пользователя в БД"""
    try:
        with Session(engine) as session:
            user: Optional[User] = session.get(User, user_id)
            if not user:
                return None

            # Обновляем только переданные поля
            if email is not None:
                user.email = email
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if avatar is not None:
                user.avatar = avatar

            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return None


def delete_user(user_id: int) -> bool:
    """Удалить пользователя из БД"""
    try:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user:
                return False

            session.delete(user)
            session.commit()
            return True
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return False


def user_exists(user_id: int) -> bool:
    """Проверить существование пользователя"""
    try:
        with Session(engine) as session:
            user = session.get(User, user_id)
            return user is not None
    except Exception as e:
        logger.error(f"Error checking user existence {user_id}: {e}")
        return False


def get_users_count() -> int:
    """Получить общее количество пользователей"""
    try:
        with Session(engine) as session:
            count = session.exec(select(func.count(User.id))).one()
            return count
    except Exception as e:
        logger.error(f"Error getting users count: {e}")
        return 0
