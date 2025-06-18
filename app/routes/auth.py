from email_validator import validate_email, EmailNotValidError
from app.exceptions import ValidationError
from fastapi import APIRouter
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/register", status_code=201, tags=["Authentication"])
def register_user(user_data: dict) -> dict:
    """Регистрация пользователя"""
    email = user_data.get("email")
    password = user_data.get("password")

    # Проверяем наличие email
    if not email:
        raise ValidationError("Missing email")

    # Валидация email
    try:
        validate_email(email)
    except EmailNotValidError:
        raise ValidationError("Invalid email format")

    # Проверяем наличие пароля
    if not password:
        raise ValidationError("Missing password")

    # Успешная регистрация (имитация)
    user_id = random.randint(1, 10)
    token = "QpwL5tke4Pnpja7X4"

    return {"id": user_id, "token": token}


@router.post("/api/login", tags=["Authentication"])
def login_user(user_data: dict) -> dict:
    """Вход пользователя"""
    email = user_data.get("email")
    password = user_data.get("password")

    # Проверяем наличие email
    if not email:
        raise ValidationError("Missing email")

    # Валидация email
    try:
        validate_email(email)
    except EmailNotValidError:
        raise ValidationError("Invalid email format")

    # Проверяем наличие пароля
    if not password:
        raise ValidationError("Missing password")

    # Успешный логин (имитация)
    token = "QpwL5tke4Pnpja7X4"

    return {"token": token}
