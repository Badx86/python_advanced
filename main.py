from fastapi import FastAPI, HTTPException
import math
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# 12 users
users = [
    {
        "id": 1,
        "email": "george.bluth@reqres.in",
        "first_name": "George",
        "last_name": "Bluth",
        "avatar": "https://reqres.in/img/faces/1-image.jpg",
    },
    {
        "id": 2,
        "email": "janet.weaver@reqres.in",
        "first_name": "Janet",
        "last_name": "Weaver",
        "avatar": "https://reqres.in/img/faces/2-image.jpg",
    },
    {
        "id": 3,
        "email": "emma.wong@reqres.in",
        "first_name": "Emma",
        "last_name": "Wong",
        "avatar": "https://reqres.in/img/faces/3-image.jpg",
    },
    {
        "id": 4,
        "email": "eve.holt@reqres.in",
        "first_name": "Eve",
        "last_name": "Holt",
        "avatar": "https://reqres.in/img/faces/4-image.jpg",
    },
    {
        "id": 5,
        "email": "charles.morris@reqres.in",
        "first_name": "Charles",
        "last_name": "Morris",
        "avatar": "https://reqres.in/img/faces/5-image.jpg",
    },
    {
        "id": 6,
        "email": "tracey.ramos@reqres.in",
        "first_name": "Tracey",
        "last_name": "Ramos",
        "avatar": "https://reqres.in/img/faces/6-image.jpg",
    },
    {
        "id": 7,
        "email": "michael.lawson@reqres.in",
        "first_name": "Michael",
        "last_name": "Lawson",
        "avatar": "https://reqres.in/img/faces/7-image.jpg",
    },
    {
        "id": 8,
        "email": "lindsay.ferguson@reqres.in",
        "first_name": "Lindsay",
        "last_name": "Ferguson",
        "avatar": "https://reqres.in/img/faces/8-image.jpg",
    },
    {
        "id": 9,
        "email": "tobias.funke@reqres.in",
        "first_name": "Tobias",
        "last_name": "Funke",
        "avatar": "https://reqres.in/img/faces/9-image.jpg",
    },
    {
        "id": 10,
        "email": "byron.fields@reqres.in",
        "first_name": "Byron",
        "last_name": "Fields",
        "avatar": "https://reqres.in/img/faces/10-image.jpg",
    },
    {
        "id": 11,
        "email": "george.edwards@reqres.in",
        "first_name": "George",
        "last_name": "Edwards",
        "avatar": "https://reqres.in/img/faces/11-image.jpg",
    },
    {
        "id": 12,
        "email": "rachel.howell@reqres.in",
        "first_name": "Rachel",
        "last_name": "Howell",
        "avatar": "https://reqres.in/img/faces/12-image.jpg",
    },
]


@app.get("/api/users")
def get_users(page: int = 1, per_page: int = 6):
    logger.info(f"Getting users list: page={page}, per_page={per_page}")

    total = len(users)
    total_pages = math.ceil(total / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    page_users = users[start:end]

    logger.info(f"Returning {len(page_users)} users for page {page}")
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "data": page_users,
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


@app.get("/api/users/{user_id}")
def get_single_user(user_id: int):
    logger.info(f"Getting single user: user_id={user_id}")

    # Ищем пользователя по ID
    user = None
    for u in users:
        if u["id"] == user_id:
            user = u
            break

    if not user:
        logger.warning(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail={})

    logger.info(f"Found user: {user['first_name']} {user['last_name']}")
    return {
        "data": user,
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


if __name__ == "__main__":
    logger.info("🚀 Starting server...")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
