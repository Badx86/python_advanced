import logging
import random
from http import HTTPStatus
from fastapi import APIRouter, HTTPException
from email_validator import validate_email, EmailNotValidError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/register", status_code=HTTPStatus.CREATED, tags=["Authentication"])
def register_user(user_data: dict) -> dict:
    """Регистрация пользователя"""
    email = user_data.get("email")
    password = user_data.get("password")

    logger.info(f"Registering user: email={email}")

    # Проверяем наличие email
    if not email:
        logger.warning("Registration failed: missing email")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail={"error": "Missing email"}
        )

    # Валидация email
    try:
        validate_email(email)
    except EmailNotValidError:
        logger.warning(f"Registration failed for {email}: invalid email format")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail={"error": "Invalid email format"}
        )

    # Проверяем наличие пароля
    if not password:
        logger.warning(f"Registration failed for {email}: missing password")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail={"error": "Missing password"}
        )

    # Успешная регистрация (имитация)
    user_id = random.randint(1, 10)
    token = "QpwL5tke4Pnpja7X4"

    logger.info(f"User registered successfully: id={user_id}")
    return {"id": user_id, "token": token}


@router.post("/api/login", tags=["Authentication"])
def login_user(user_data: dict) -> dict:
    """Вход пользователя"""
    email = user_data.get("email")
    password = user_data.get("password")

    logger.info(f"Login attempt: email={email}")

    # Проверяем наличие email
    if not email:
        logger.warning("Login failed: missing email")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail={"error": "Missing email"}
        )

    # Валидация email
    try:
        validate_email(email)
    except EmailNotValidError:
        logger.warning(f"Login failed for {email}: invalid email format")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail={"error": "Invalid email format"}
        )

    # Проверяем наличие пароля
    if not password:
        logger.warning(f"Login failed for {email}: missing password")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail={"error": "Missing password"}
        )

    # Успешный логин (имитация)
    token = "QpwL5tke4Pnpja7X4"

    logger.info(f"User logged in successfully: {email}")
    return {"token": token}
