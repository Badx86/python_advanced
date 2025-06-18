from sqlmodel import create_engine, SQLModel
import logging
import os

logger = logging.getLogger(__name__)

# Получаем настройки из переменных окружения
DATABASE_URL = os.getenv("DATABASE_ENGINE")
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", 10))

if not DATABASE_URL:
    raise ValueError("DATABASE_ENGINE environment variable is not set")

try:
    engine = create_engine(
        DATABASE_URL,
        pool_size=DATABASE_POOL_SIZE,
        echo=False,  # True для отладки SQL запросов
    )
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise


def create_db_and_tables() -> None:
    """Создает базу данных и таблицы, если они не существуют"""
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
