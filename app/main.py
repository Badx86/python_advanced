from email_validator import validate_email, EmailNotValidError
from fastapi import FastAPI, HTTPException, Query
from fastapi_pagination import Page
from typing import Dict, Any, List
from dotenv import load_dotenv
from datetime import datetime
from http import HTTPStatus
import logging
import random
import time
import os
from app.models import (
    CreateUserRequest,
    CreateUserResponse,
    UpdateUserRequest,
    UpdateUserResponse,
    User,
    Resource,
    AppStatus,
)

# Загружаем переменные окружения
load_dotenv()

# Получаем настройки из .env
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("api.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FastAPI Reqres Clone",
    description="Микросервис-клон Reqres API для тестирования",
    version="1.0.0",
)

users_data = [
    User(
        id=1,
        email="george.bluth@reqres.in",
        first_name="George",
        last_name="Bluth",
        avatar="https://reqres.in/img/faces/1-image.jpg",
    ),
    User(
        id=2,
        email="janet.weaver@reqres.in",
        first_name="Janet",
        last_name="Weaver",
        avatar="https://reqres.in/img/faces/2-image.jpg",
    ),
    User(
        id=3,
        email="emma.wong@reqres.in",
        first_name="Emma",
        last_name="Wong",
        avatar="https://reqres.in/img/faces/3-image.jpg",
    ),
    User(
        id=4,
        email="eve.holt@reqres.in",
        first_name="Eve",
        last_name="Holt",
        avatar="https://reqres.in/img/faces/4-image.jpg",
    ),
    User(
        id=5,
        email="charles.morris@reqres.in",
        first_name="Charles",
        last_name="Morris",
        avatar="https://reqres.in/img/faces/5-image.jpg",
    ),
    User(
        id=6,
        email="tracey.ramos@reqres.in",
        first_name="Tracey",
        last_name="Ramos",
        avatar="https://reqres.in/img/faces/6-image.jpg",
    ),
    User(
        id=7,
        email="michael.lawson@reqres.in",
        first_name="Michael",
        last_name="Lawson",
        avatar="https://reqres.in/img/faces/7-image.jpg",
    ),
    User(
        id=8,
        email="lindsay.ferguson@reqres.in",
        first_name="Lindsay",
        last_name="Ferguson",
        avatar="https://reqres.in/img/faces/8-image.jpg",
    ),
    User(
        id=9,
        email="tobias.funke@reqres.in",
        first_name="Tobias",
        last_name="Funke",
        avatar="https://reqres.in/img/faces/9-image.jpg",
    ),
    User(
        id=10,
        email="byron.fields@reqres.in",
        first_name="Byron",
        last_name="Fields",
        avatar="https://reqres.in/img/faces/10-image.jpg",
    ),
    User(
        id=11,
        email="george.edwards@reqres.in",
        first_name="George",
        last_name="Edwards",
        avatar="https://reqres.in/img/faces/11-image.jpg",
    ),
    User(
        id=12,
        email="rachel.howell@reqres.in",
        first_name="Rachel",
        last_name="Howell",
        avatar="https://reqres.in/img/faces/12-image.jpg",
    ),
]

resources_data = [
    Resource(
        id=1, name="cerulean", year=2000, color="#98B2D1", pantone_value="15-4020"
    ),
    Resource(
        id=2, name="fuchsia rose", year=2001, color="#C74375", pantone_value="17-2031"
    ),
    Resource(
        id=3, name="true red", year=2002, color="#BF1932", pantone_value="19-1664"
    ),
    Resource(
        id=4, name="aqua sky", year=2003, color="#7BC4C4", pantone_value="14-4811"
    ),
    Resource(
        id=5, name="tigerlily", year=2004, color="#E2583E", pantone_value="17-1456"
    ),
    Resource(
        id=6, name="blue turquoise", year=2005, color="#53B0AE", pantone_value="15-5217"
    ),
    Resource(
        id=7, name="sand dollar", year=2006, color="#DECDBE", pantone_value="13-1106"
    ),
    Resource(
        id=8, name="chili pepper", year=2007, color="#9B1B30", pantone_value="19-1557"
    ),
    Resource(
        id=9, name="blue iris", year=2008, color="#5A5B9F", pantone_value="18-3943"
    ),
    Resource(id=10, name="mimosa", year=2009, color="#F0C05A", pantone_value="14-0848"),
    Resource(
        id=11, name="turquoise", year=2010, color="#45B5AA", pantone_value="15-5519"
    ),
    Resource(
        id=12, name="honeysuckle", year=2011, color="#D94F70", pantone_value="18-2120"
    ),
]


def paginate_data(data: List[Any], page: int, size: int) -> Page[Any]:
    """Универсальная функция пагинации"""
    total = len(data)
    start_index = (page - 1) * size
    end_index = start_index + size
    items = data[start_index:end_index]
    total_pages = (total + size - 1) // size

    return Page(items=items, page=page, size=size, total=total, pages=total_pages)


def find_user_by_id(user_id: int) -> User | None:
    """Поиск пользователя по ID"""
    return next((user for user in users_data if user.id == user_id), None)


def find_resource_by_id(resource_id: int) -> Resource | None:
    """Поиск ресурса по ID"""
    return next(
        (resource for resource in resources_data if resource.id == resource_id), None
    )


@app.get("/status", tags=["System"])
def get_status() -> AppStatus:
    """Проверка статуса приложения"""
    logger.info("Health check requested")
    return AppStatus(users=bool(users_data), resources=bool(resources_data))


@app.get("/api/users", tags=["Users"])
def get_users(
    page: int = Query(1, ge=1), size: int = Query(6, ge=1, le=50, alias="per_page")
) -> Page[User]:
    """Получить список пользователей с пагинацией"""
    logger.info(f"Getting users list: page={page}, per_page={size}")
    users_page = paginate_data(users_data, page, size)
    logger.info(f"Returning {len(users_page.items)} users for page {page}")
    return users_page


@app.get("/api/users/{user_id}", tags=["Users"])
def get_single_user(user_id: int) -> Dict[str, Any]:
    """Получить пользователя по ID"""
    logger.info(f"Getting single user: user_id={user_id}")
    user = find_user_by_id(user_id)
    if not user:
        logger.warning(f"User {user_id} not found")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"User {user_id} not found"},
        )

    logger.info(f"Found user: {user.first_name} {user.last_name}")
    return {
        "data": user.model_dump(),
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


@app.get("/api/unknown", tags=["Resources"])
def get_resources(
    page: int = Query(1, ge=1), size: int = Query(6, ge=1, le=50, alias="per_page")
) -> Page[Resource]:
    """Получить список ресурсов с пагинацией"""
    logger.info(f"Getting resources list: page={page}, per_page={size}")
    resources_page = paginate_data(resources_data, page, size)
    logger.info(f"Returning {len(resources_page.items)} resources for page {page}")
    return resources_page


@app.get("/api/unknown/{resource_id}", tags=["Resources"])
def get_single_resource(resource_id: int) -> Dict[str, Any]:
    """Получить ресурс по ID"""
    logger.info(f"Getting single resource: resource_id={resource_id}")
    resource = find_resource_by_id(resource_id)
    if not resource:
        logger.warning(f"Resource {resource_id} not found")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Resource {resource_id} not found"},
        )

    logger.info(f"Found resource: {resource.name} ({resource.year})")
    return {
        "data": resource.model_dump(),
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


@app.post("/api/users", status_code=HTTPStatus.CREATED, tags=["Users"])
def create_user(user_data: CreateUserRequest) -> CreateUserResponse:
    """Создать нового пользователя"""
    logger.info(f"Creating user: name={user_data.name}, job={user_data.job}")
    new_id = str(random.randint(100, 9999))
    created_at = datetime.now()
    logger.info(f"Created user with ID: {new_id}")
    return CreateUserResponse(
        name=user_data.name, job=user_data.job, id=new_id, createdAt=created_at
    )


@app.put("/api/users/{user_id}", tags=["Users"])
def update_user_put(user_id: int, user_data: UpdateUserRequest) -> UpdateUserResponse:
    """Полное обновление пользователя"""
    logger.info(
        f"PUT updating user {user_id}: name={user_data.name}, job={user_data.job}"
    )
    updated_at = datetime.now()
    logger.info(f"Updated user {user_id}")
    return UpdateUserResponse(
        name=user_data.name, job=user_data.job, updatedAt=updated_at
    )


@app.patch("/api/users/{user_id}", tags=["Users"])
def update_user_patch(user_id: int, user_data: UpdateUserRequest) -> UpdateUserResponse:
    """Частичное обновление пользователя"""
    logger.info(
        f"PATCH updating user {user_id}: name={user_data.name}, job={user_data.job}"
    )
    updated_at = datetime.now()
    logger.info(f"Patched user {user_id}")
    return UpdateUserResponse(
        name=user_data.name, job=user_data.job, updatedAt=updated_at
    )


@app.delete("/api/users/{user_id}", status_code=HTTPStatus.NO_CONTENT, tags=["Users"])
def delete_user(user_id: int) -> None:
    """Удалить пользователя"""
    logger.info(f"Deleting user {user_id}")


@app.post("/api/register", status_code=HTTPStatus.CREATED, tags=["Authentication"])
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


@app.post("/api/login", tags=["Authentication"])
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


@app.get("/api/users", tags=["Users"])
def get_users_with_delay(
    page: int = Query(1, ge=1),
    size: int = Query(6, ge=1, le=50, alias="per_page"),
    delay: int = Query(0, ge=0, le=10),
) -> Dict[str, Any]:
    """Получить список пользователей с пагинацией и опциональной задержкой"""
    logger.info(f"Getting users list: page={page}, per_page={size}, delay={delay}")

    # Добавляем задержку если указана
    if delay > 0:
        logger.info(f"Applying delay: {delay} seconds")
        time.sleep(delay)

    users_page = paginate_data(users_data, page, size)
    logger.info(f"Returning {len(users_page.items)} users for page {page}")

    return {
        "page": users_page.page,
        "per_page": users_page.size,
        "total": users_page.total,
        "total_pages": users_page.pages,
        "data": [user.model_dump() for user in users_page.items],
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


if __name__ == "__main__":
    logger.info(f"Starting server on {HOST}:{PORT}...")
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
