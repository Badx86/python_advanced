from typing import Iterable, Optional
from sqlmodel import Session, select, func
from fastapi_pagination import Page
from app.database.engine import engine
from app.models import User
import logging

logger = logging.getLogger(__name__)


def get_user(user_id: int) -> Optional[User]:
    """Поиск пользователя по ID"""
    try:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if user:
                logger.info(f"Found user: {user.first_name} {user.last_name}")
            else:
                logger.warning(f"User {user_id} not found in database")
            return user
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None


def get_users_paginated(page: int = 1, size: int = 6) -> Page[User]:
    """Получить список пользователей с пагинацией"""
    try:
        with Session(engine) as session:
            # Подсчет общего количества пользователей
            total_count = session.exec(select(func.count(User.id))).one()

            # Получение пользователей для текущей страницы
            offset = (page - 1) * size
            statement = select(User).offset(offset).limit(size)
            users = session.exec(statement).all()

            # Подсчет общего количества страниц
            total_pages = (total_count + size - 1) // size

            logger.info(f"Retrieved {len(users)} users for page {page}")

            return Page(
                items=users, page=page, size=size, total=total_count, pages=total_pages
            )
    except Exception as e:
        logger.error(f"Error getting users page {page}: {e}")
        # Возвращаем пустую страницу в случае ошибки
        return Page(items=[], page=page, size=size, total=0, pages=0)


def get_all_users() -> Iterable[User]:
    """Получить всех пользователей (для системных нужд)"""
    try:
        with Session(engine) as session:
            statement = select(User)
            users = session.exec(statement).all()
            logger.info(f"Retrieved {len(list(users))} total users")
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

            logger.info(
                f"Created user: {new_user.first_name} {new_user.last_name} (ID: {new_user.id})"
            )
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
                logger.warning(f"User {user_id} not found for update")
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

            logger.info(f"Updated user {user_id}: {user.first_name} {user.last_name}")
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
                logger.warning(f"User {user_id} not found for deletion")
                return False

            session.delete(user)
            session.commit()

            logger.info(f"Deleted user {user_id}: {user.first_name} {user.last_name}")
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
