import logging
from datetime import datetime
from http import HTTPStatus
from typing import Dict, Any
from app.database.resources import get_resources_paginated
from app.models import Resource
from fastapi import Depends
from fastapi_pagination import Page, Params
from fastapi import APIRouter, HTTPException
from app.models import (
    CreateResourceRequest,
    CreateResourceResponse,
    UpdateResourceRequest,
    UpdateResourceResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/unknown", tags=["Resources"])
def get_resources(params: Params = Depends()) -> Page[Resource]:
    logger.info(f"[API] Getting resources list: page={params.page}, size={params.size}")

    resources_page = get_resources_paginated(page=params.page, size=params.size)

    logger.info(
        f"[API] Returning {len(resources_page.items)} resources for page={params.page}"
    )

    return resources_page


@router.get("/api/unknown/{resource_id}", tags=["Resources"])
def get_single_resource(resource_id: int) -> Dict[str, Any]:
    """Получить ресурс по ID"""
    logger.info(f"[API] Getting single resource: resource_id={resource_id}")

    # Валидация ID
    if resource_id < 1:
        logger.warning(f"[API] Invalid resource ID: {resource_id}")
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid resource ID"
        )

    from app.database.resources import get_resource

    resource = get_resource(resource_id)
    if not resource:
        logger.warning(f"[API] Resource {resource_id} not found")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Resource {resource_id} not found"},
        )

    logger.info(f"[API] Found resource: {resource.name} ({resource.year})")
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
    logger.info(f"[API] Creating resource: {resource_data.name} ({resource_data.year})")

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
        logger.error(f"[API] Failed to create resource in database")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Failed to create resource",
        )

    # Возвращаем ответ в формате API
    created_at = datetime.now()
    logger.info(f"[API] Created resource with ID: {db_resource.id}")
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
    logger.info(f"[API] PUT updating resource {resource_id}")

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
        logger.warning(f"[API] Resource {resource_id} not found for update")
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
    logger.info(f"[API] Updated resource {resource_id}")
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
    logger.info(f"[API] PATCH updating resource {resource_id}")

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
        logger.warning(f"[API] Resource {resource_id} not found for update")
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
    logger.info(f"[API] Patched resource {resource_id}")
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
    logger.info(f"[API] Deleting resource {resource_id}")

    # Валидация ID
    if resource_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid resource ID"
        )

    from app.database.resources import delete_resource as db_delete_resource

    # Удаляем из БД
    deleted = db_delete_resource(resource_id)

    # Корректное поведение - 404 если ресурса не было
    if not deleted:
        logger.warning(f"[API] Resource {resource_id} not found for deletion")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"error": f"Resource {resource_id} not found"},
        )

    logger.info(f"[API] Resource {resource_id} deleted successfully")
