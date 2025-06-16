import json
import logging
from pathlib import Path
from app.database.users import get_users_count, create_user

logger = logging.getLogger(__name__)


def seed_users_data():
    """Загружает тестовых пользователей из JSON в БД если БД пустая"""
    try:
        # Проверяем, есть ли уже пользователи в БД
        users_count = get_users_count()
        if users_count > 0:
            logger.info(f"Database already has {users_count} users, skipping seed")
            return

        # Загружаем данные из JSON
        json_path = Path("app/data/users.json")
        if not json_path.exists():
            logger.warning("users.json not found, skipping seed")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            users_data = json.load(f)

        # Создаем пользователей в БД
        created_count = 0
        for user_json in users_data:
            user = create_user(
                email=user_json["email"],
                first_name=user_json["first_name"],
                last_name=user_json["last_name"],
                avatar=user_json["avatar"],
            )
            if user:
                created_count += 1
                logger.debug(f"Created user: {user.first_name} {user.last_name}")

        logger.info(f"Successfully seeded {created_count} users from JSON to database")

    except Exception as e:
        logger.error(f"Error seeding users data: {e}")


def seed_resources_data():
    """Загружает тестовые ресурсы из JSON в БД если БД пустая"""
    try:
        from app.database.resources import get_resources_count, create_resource

        # Проверяем, есть ли уже ресурсы в БД
        resources_count = get_resources_count()
        if resources_count > 0:
            logger.info(
                f"Database already has {resources_count} resources, skipping seed"
            )
            return

        # Загружаем данные из JSON
        json_path = Path("app/data/resources.json")
        if not json_path.exists():
            logger.warning("resources.json not found, skipping seed")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            resources_data = json.load(f)

        # Создаем ресурсы в БД
        created_count = 0
        for resource_json in resources_data:
            resource = create_resource(
                name=resource_json["name"],
                year=resource_json["year"],
                color=resource_json["color"],
                pantone_value=resource_json["pantone_value"],
            )
            if resource:
                created_count += 1
                logger.debug(f"Created resource: {resource.name} ({resource.year})")

        logger.info(
            f"Successfully seeded {created_count} resources from JSON to database"
        )

    except Exception as e:
        logger.error(f"Error seeding resources data: {e}")


# Обновить функцию seed_all_data():
def seed_all_data():
    """Загружает все тестовые данные"""
    logger.info("Starting data seeding...")
    seed_users_data()
    seed_resources_data()
    logger.info("Data seeding completed")
