from email_validator import validate_email, EmailNotValidError
from app.exceptions import ValidationError
from app.models import RegisterRequest, LoginRequest, RegisterResponse, LoginResponse
from fastapi import APIRouter
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/api/register",
    status_code=201,
    tags=["Authentication"],
    response_model=RegisterResponse,
)
def register_user(request: RegisterRequest) -> RegisterResponse:
    """Регистрация пользователя"""

    # Проверяем наличие email
    if not request.email.strip():
        raise ValidationError("Missing email")

    # Валидация email
    try:
        validate_email(request.email)
    except EmailNotValidError:
        raise ValidationError("Invalid email format")

    # Проверяем наличие пароля
    if not request.password.strip():
        raise ValidationError("Missing password")

    # Успешная регистрация (имитация)
    user_id = random.randint(1, 10)
    token = "QpwL5tke4Pnpja7X4"

    return RegisterResponse(id=user_id, token=token)


@router.post("/api/login", tags=["Authentication"], response_model=LoginResponse)
def login_user(request: LoginRequest) -> LoginResponse:
    """Вход пользователя"""

    # Проверяем наличие email
    if not request.email.strip():
        raise ValidationError("Missing email")

    # Валидация email
    try:
        validate_email(request.email)
    except EmailNotValidError:
        raise ValidationError("Invalid email format")

    # Проверяем наличие пароля
    if not request.password.strip():
        raise ValidationError("Missing password")

    # Успешный логин (имитация)
    token = "QpwL5tke4Pnpja7X4"

    return LoginResponse(token=token)
