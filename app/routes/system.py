import os
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from app.models import HealthStatus
from app.database.users import get_users_count

logger = logging.getLogger(__name__)

router = APIRouter()

# Загружаем данные из JSON для проверки статуса ресурсов
with open("app/data/resources.json", "r", encoding="utf-8") as f:
    resources_data = json.load(f)


def get_app_version():
    """Получает версию из pyproject.toml или переменной окружения"""
    version = os.getenv("APP_VERSION")
    if version:
        return version

    try:
        import toml

        with open("pyproject.toml", "r") as f:
            data = toml.load(f)
            return data["tool"]["poetry"]["version"]
    except:
        return "unknown"


def get_database_type():
    """Определяет тип БД из connection string"""
    db_url = os.getenv("DATABASE_ENGINE", "")
    if "postgresql" in db_url:
        return "postgresql"
    elif "sqlite" in db_url:
        return "sqlite"
    elif "mysql" in db_url:
        return "mysql"
    else:
        return "unknown"


def check_database_connection():
    """Проверяет подключение к БД"""
    try:
        # Проверка подключения
        users_count = get_users_count()
        return True, users_count
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False, 0


@router.get("/status", tags=["System"])
def get_status() -> HealthStatus:
    """Проверка статуса приложения с подробной информацией"""
    logger.info("Health check requested")

    # Получаем текущее время
    current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Проверяем подключение к БД
    db_connected, users_count = check_database_connection()

    # Проверяем наличие данных ресурсов
    resources_count = len(resources_data)
    resources_status = resources_count > 0

    # Определяем общий статус
    overall_status = "healthy" if db_connected and resources_status else "unhealthy"

    logger.info(
        f"Status check: users={users_count} (db_connected: {db_connected}), resources={resources_count}"
    )

    # Создаем структурированный ответ
    return HealthStatus(
        status=overall_status,
        timestamp=current_time,
        version=get_app_version(),
        database={
            "status": "connected" if db_connected else "disconnected",
            "type": get_database_type(),
            "users_count": users_count,
        },
        data={
            "users": {"loaded": users_count > 0, "count": users_count},
            "resources": {"loaded": resources_status, "count": resources_count},
        },
        services={"api": "running", "database": get_database_type()},
    )
