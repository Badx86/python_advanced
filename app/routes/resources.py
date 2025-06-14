import json
import logging
from http import HTTPStatus
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from fastapi_pagination import Page
from app.models import Resource

logger = logging.getLogger(__name__)

router = APIRouter()

# Загружаем ресурсы из JSON
with open("app/data/resources.json", "r", encoding="utf-8") as f:
    resources_json = json.load(f)
    resources_data = [Resource(**resource) for resource in resources_json]


def paginate_data(data, page: int, size: int) -> Page:
    """Универсальная функция пагинации"""
    total = len(data)
    start_index = (page - 1) * size
    end_index = start_index + size
    items = data[start_index:end_index]
    total_pages = (total + size - 1) // size

    return Page(items=items, page=page, size=size, total=total, pages=total_pages)


def find_resource_by_id(resource_id: int) -> Resource | None:
    """Поиск ресурса по ID"""
    return next(
        (resource for resource in resources_data if resource.id == resource_id), None
    )


@router.get("/api/unknown", tags=["Resources"])
def get_resources(
    page: int = Query(1, ge=1), size: int = Query(6, ge=1, le=50, alias="per_page")
) -> Page[Resource]:
    """Получить список ресурсов с пагинацией"""
    logger.info(f"Getting resources list: page={page}, per_page={size}")
    resources_page = paginate_data(resources_data, page, size)
    logger.info(f"Returning {len(resources_page.items)} resources for page {page}")
    return resources_page


@router.get("/api/unknown/{resource_id}", tags=["Resources"])
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
