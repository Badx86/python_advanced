from app.routes import users, resources, auth, system
from dotenv import load_dotenv
from fastapi import FastAPI
import logging
import os

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

# Подключаем роуты
app.include_router(system.router)
app.include_router(users.router)
app.include_router(resources.router)
app.include_router(auth.router)

if __name__ == "__main__":
    logger.info(f"Starting server on {HOST}:{PORT}...")
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
