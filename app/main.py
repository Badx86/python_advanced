from dotenv import load_dotenv
import os
import sys

# Добавляем корневую папку в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(".env")

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting application...")
    create_db_and_tables()
    logger.info("Database initialized successfully")

    # Загружаем тестовые данные если БД пустая
    seed_all_data()

    yield
    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(
    title="FastAPI Reqres Clone",
    description="Микросервис-клон Reqres API для тестирования",
    version="1.0.0",
    lifespan=lifespan,
)

# Подключаем роуты
app.include_router(system.router)
app.include_router(users.router)
app.include_router(resources.router)
app.include_router(auth.router)

if __name__ == "__main__":
    logger.info(f"Starting server on {HOST}:{PORT}...")
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
