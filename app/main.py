from typing import AsyncGenerator
from dotenv import load_dotenv
import os
import sys

# Добавляем корневую папку в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(".env")

from fastapi_pagination import add_pagination
from app.database.engine import create_db_and_tables
from app.database.seed import seed_all_data
from app.routes import users, resources, auth, system
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Получаем настройки из .env
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Настройка логгера
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
# Для включения DB логов: SHOW_DB_LOGS=true + LOG_LEVEL=DEBUG в .env
show_db = os.getenv("SHOW_DB_LOGS", "false").lower() == "true"

logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("api.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# Настраиваем DB логи
if show_db:
    logging.getLogger("app").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting application...")

    try:
        create_db_and_tables()
        seed_all_data()
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(
    title="FastAPI Reqres",
    description="Микросервис Reqres API для тестирования",
    version="1.0.0",
    lifespan=lifespan,
)

add_pagination(app)

# Подключаем роуты
app.include_router(system.router)
app.include_router(users.router)
app.include_router(resources.router)
app.include_router(auth.router)

if __name__ == "__main__":
    logger.info(f"Starting server on {HOST}:{PORT}...")
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
