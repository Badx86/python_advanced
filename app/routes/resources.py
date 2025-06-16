import logging
from datetime import datetime
from http import HTTPStatus
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.models import (
    CreateResourceRequest,
    CreateResourceResponse,
    UpdateResourceRequest,
    UpdateResourceResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/unknown", tags=["Resources"])
def get_resources(
    page: int = Query(1, ge=1), size: int = Query(6, ge=1, le=50, alias="per_page")
):
    """Получить список ресурсов с пагинацией"""
    logger.info(f"Getting resources list: page={page}, per_page={size}")

    from app.database.resources import get_resources_paginated

    resources_page = get_resources_paginated(page=page, size=size)
    logger.info(f"Returning {len(resources_page.items)} resources for page {page}")
    return resources_page


@router.get("/api/unknown/{resource_id}", tags=["Resources"])
def get_single_resource(resource_id: int) -> Dict[str, Any]:
    """Получить ресурс по ID"""
    logger.info(f"Getting single resource: resource_id={resource_id}")

    # Валидация ID
    if resource_id < 1:
        logger.warning(f"Invalid resource ID: {resource_id}")
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid resource ID"
        )

    from app.database.resources import get_resource

    resource = get_resource(resource_id)
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


@router.post("/api/unknown", status_code=HTTPStatus.CREATED, tags=["Resources"])
def create_resource(resource_data: CreateResourceRequest) -> CreateResourceResponse:
    """Создать новый ресурс"""
    logger.info(f"Creating resource: {resource_data.name} ({resource_data.year})")

    # Валидация данных
    if not resource_data.name or not resource_data.name.strip():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Name is required"
        )
    if resource_data.year < 1900 or resource_data.year > 2100:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid year")

    from app.database.resources import create_resource as db_create_resource

    # Сохраняем в БД
    db_resource = db_create_resource(
        name=resource_data.name,
        year=resource_data.year,
        color=resource_data.color,
        pantone_value=resource_data.pantone_value,
    )

    if not db_resource:
        logger.error(f"Failed to create resource in database")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Failed to create resource",
        )

    # Возвращаем ответ в формате API
    created_at = datetime.now()
    logger.info(f"Created resource with ID: {db_resource.id}")
    return CreateResourceResponse(
        name=resource_data.name,
        year=resource_data.year,
        color=resource_data.color,
        pantone_value=resource_data.pantone_value,
        id=str(db_resource.id),
        createdAt=created_at,
    )


@router.put("/api/unknown/{resource_id}", tags=["Resources"])
def update_resource_put(
    resource_id: int, resource_data: UpdateResourceRequest
) -> UpdateResourceResponse:
    """Полное обновление ресурса"""
    logger.info(f"PUT updating resource {resource_id}")

    # Валидация ID
    if resource_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid resource ID"
        )

    # Проверяем существование ресурса
    from app.database.resources import (
        get_resource,
        update_resource as db_update_resource,
    )

    existing_resource = get_resource(resource_id)
    if not existing_resource:
        logger.warning(f"Resource {resource_id} not found for update")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Resource {resource_id} not found"},
        )

    # Обновляем ресурс в БД
    db_update_resource(
        resource_id=resource_id,
        name=resource_data.name,
        year=resource_data.year,
        color=resource_data.color,
        pantone_value=resource_data.pantone_value,
    )

    updated_at = datetime.now()
    logger.info(f"Updated resource {resource_id}")
    return UpdateResourceResponse(
        name=resource_data.name,
        year=resource_data.year,
        color=resource_data.color,
        pantone_value=resource_data.pantone_value,
        updatedAt=updated_at,
    )


@router.patch("/api/unknown/{resource_id}", tags=["Resources"])
def update_resource_patch(
    resource_id: int, resource_data: UpdateResourceRequest
) -> UpdateResourceResponse:
    """Частичное обновление ресурса"""
    logger.info(f"PATCH updating resource {resource_id}")

    # Валидация ID
    if resource_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid resource ID"
        )

    # Проверяем существование ресурса
    from app.database.resources import (
        get_resource,
        update_resource as db_update_resource,
    )

    existing_resource = get_resource(resource_id)
    if not existing_resource:
        logger.warning(f"Resource {resource_id} not found for update")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Resource {resource_id} not found"},
        )

    # Частичное обновление в БД
    db_update_resource(
        resource_id=resource_id,
        name=resource_data.name,
        year=resource_data.year,
        color=resource_data.color,
        pantone_value=resource_data.pantone_value,
    )

    updated_at = datetime.now()
    logger.info(f"Patched resource {resource_id}")
    return UpdateResourceResponse(
        name=resource_data.name,
        year=resource_data.year,
        color=resource_data.color,
        pantone_value=resource_data.pantone_value,
        updatedAt=updated_at,
    )


@router.delete(
    "/api/unknown/{resource_id}", status_code=HTTPStatus.NO_CONTENT, tags=["Resources"]
)
def delete_resource(resource_id: int) -> None:
    """Удалить ресурс"""
    logger.info(f"Deleting resource {resource_id}")

    # Валидация ID
    if resource_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid resource ID"
        )

    from app.database.resources import delete_resource as db_delete_resource

    # Удаляем из БД
    deleted = db_delete_resource(resource_id)

    if not deleted:
        logger.warning(f"Resource {resource_id} not found for deletion")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Resource {resource_id} not found"},
        )

    logger.info(f"Resource {resource_id} deleted successfully")
