from fastapi import FastAPI, HTTPException
import math
import logging
from typing import Dict, Any, List

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("api.log", encoding="utf-8"),  # в файл
        logging.StreamHandler(),  # в консоль
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI()

users: List[Dict[str, Any]] = [
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

resources: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "cerulean",
        "year": 2000,
        "color": "#98B2D1",
        "pantone_value": "15-4020",
    },
    {
        "id": 2,
        "name": "fuchsia rose",
        "year": 2001,
        "color": "#C74375",
        "pantone_value": "17-2031",
    },
    {
        "id": 3,
        "name": "true red",
        "year": 2002,
        "color": "#BF1932",
        "pantone_value": "19-1664",
    },
    {
        "id": 4,
        "name": "aqua sky",
        "year": 2003,
        "color": "#7BC4C4",
        "pantone_value": "14-4811",
    },
    {
        "id": 5,
        "name": "tigerlily",
        "year": 2004,
        "color": "#E2583E",
        "pantone_value": "17-1456",
    },
    {
        "id": 6,
        "name": "blue turquoise",
        "year": 2005,
        "color": "#53B0AE",
        "pantone_value": "15-5217",
    },
    {
        "id": 7,
        "name": "sand dollar",
        "year": 2006,
        "color": "#DECDBE",
        "pantone_value": "13-1106",
    },
    {
        "id": 8,
        "name": "chili pepper",
        "year": 2007,
        "color": "#9B1B30",
        "pantone_value": "19-1557",
    },
    {
        "id": 9,
        "name": "blue iris",
        "year": 2008,
        "color": "#5A5B9F",
        "pantone_value": "18-3943",
    },
    {
        "id": 10,
        "name": "mimosa",
        "year": 2009,
        "color": "#F0C05A",
        "pantone_value": "14-0848",
    },
    {
        "id": 11,
        "name": "turquoise",
        "year": 2010,
        "color": "#45B5AA",
        "pantone_value": "15-5519",
    },
    {
        "id": 12,
        "name": "honeysuckle",
        "year": 2011,
        "color": "#D94F70",
        "pantone_value": "18-2120",
    },
]


def find_user_by_id(user_id: int) -> Dict[str, Any] | None:
    """Поиск пользователя по ID"""
    for user in users:
        if user["id"] == user_id:
            return user
    return None


def find_resource_by_id(resource_id: int) -> Dict[str, Any] | None:
    """Поиск ресурса по ID"""
    for resource in resources:
        if resource["id"] == resource_id:
            return resource
    return None


@app.get("/api/users")
def get_users(page: int = 1, per_page: int = 6) -> Dict[str, Any]:
    """Получение списка пользователей с пагинацией"""
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
def get_single_user(user_id: int) -> Dict[str, Any]:
    """Получение одного пользователя по ID"""
    logger.info(f"Getting single user: user_id={user_id}")

    user = find_user_by_id(user_id)

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


@app.get("/api/unknown")
def get_resources(page: int = 1, per_page: int = 6) -> Dict[str, Any]:
    """Получение списка ресурсов с пагинацией"""
    logger.info(f"Getting resources list: page={page}, per_page={per_page}")

    total = len(resources)
    total_pages = math.ceil(total / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    page_resources = resources[start:end]

    logger.info(f"Returning {len(page_resources)} resources for page {page}")
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "data": page_resources,
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


@app.get("/api/unknown/{resource_id}")
def get_single_resource(resource_id: int) -> Dict[str, Any]:
    """Получение одного ресурса по ID"""
    logger.info(f"Getting single resource: resource_id={resource_id}")

    resource = find_resource_by_id(resource_id)

    if not resource:
        logger.warning(f"Resource {resource_id} not found")
        raise HTTPException(status_code=404, detail={})

    logger.info(f"Found resource: {resource['name']} ({resource['year']})")
    return {
        "data": resource,
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


if __name__ == "__main__":
    logger.info("Starting server...")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
