import json
import logging
from fastapi import APIRouter
from app.models import AppStatus

logger = logging.getLogger(__name__)

router = APIRouter()

# Загружаем данные из JSON для проверки статуса
with open("app/data/users.json", "r", encoding="utf-8") as f:
    users_data = json.load(f)

with open("app/data/resources.json", "r", encoding="utf-8") as f:
    resources_data = json.load(f)


@router.get("/status", tags=["System"])
def get_status() -> AppStatus:
    """Проверка статуса приложения"""
    logger.info("Health check requested")
    return AppStatus(users=bool(users_data), resources=bool(resources_data))
