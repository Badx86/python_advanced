import json
import logging
from pathlib import Path
from sqlmodel import Session, select, func
from app.database.engine import engine
from app.models import User, Resource

logger = logging.getLogger(__name__)


def seed_users_data() -> None:
    """Загружает тестовых пользователей из JSON в БД если БД пустая"""
    try:
        with Session(engine) as session:
            # Проверяем, есть ли уже пользователи в БД
            users_count = session.exec(select(func.count(User.id))).one()
            if users_count > 0:
                logger.info(f"Users already loaded: {users_count}")
                return

            # Загружаем данные из JSON
            json_path = Path("app/data/users.json")
            if not json_path.exists():
                logger.warning("Users JSON file not found")
                return

            with open(json_path, "r", encoding="utf-8") as f:
                users_data = json.load(f)

            # Создаем пользователей в БД
            created_count = 0
            for user_json in users_data:
                user = User(
                    email=user_json["email"],
                    first_name=user_json["first_name"],
                    last_name=user_json["last_name"],
                    avatar=user_json["avatar"],
                )
                session.add(user)
                created_count += 1

            session.commit()
            logger.info(f"Created {created_count} users in database")

    except Exception as e:
        logger.error(f"Error seeding users data: {e}")


def seed_resources_data() -> None:
    """Загружает тестовые ресурсы из JSON в БД если БД пустая"""
    try:
        with Session(engine) as session:
            # Проверяем, есть ли уже ресурсы в БД
            resources_count = session.exec(select(func.count(Resource.id))).one()
            if resources_count > 0:
                logger.info(f"Resources already loaded: {resources_count}")
                return

            # Загружаем данные из JSON
            json_path = Path("app/data/resources.json")
            if not json_path.exists():
                logger.warning("Resources JSON file not found")
                return

            with open(json_path, "r", encoding="utf-8") as f:
                resources_data = json.load(f)

            # Создаем ресурсы в БД
            created_count = 0
            for resource_json in resources_data:
                resource = Resource(
                    name=resource_json["name"],
                    year=resource_json["year"],
                    color=resource_json["color"],
                    pantone_value=resource_json["pantone_value"],
                )
                session.add(resource)
                created_count += 1

            session.commit()
            logger.info(f"Created {created_count} resources in database")

    except Exception as e:
        logger.error(f"Error seeding resources data: {e}")


def seed_all_data() -> None:
    """Загружает все тестовые данные"""
    logger.info("Starting data seeding...")
    seed_users_data()
    seed_resources_data()
    logger.info("Data seeding completed")
