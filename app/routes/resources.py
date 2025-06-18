from app.exceptions import ResourceNotFoundError, ValidationError, InvalidIDError
from app.database.resources import get_resources_paginated
from fastapi_pagination import Page, Params
from app.database.engine import engine
from app.models import Resource
from fastapi import APIRouter
from sqlmodel import Session
from datetime import datetime
from typing import Dict, Any
from fastapi import Depends
import logging
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
    """Получить список ресурсов с пагинацией"""

    # Создаем session и передаем в database функцию
    with Session(engine) as session:
        resources_page = get_resources_paginated(session)

    return resources_page


@router.get("/api/unknown/{resource_id}", tags=["Resources"])
def get_single_resource(resource_id: int) -> Dict[str, Any]:
    """Получить ресурс по ID"""

    # Валидация ID
    if resource_id < 1:
        raise InvalidIDError("resource ID")

    from app.database.resources import get_resource

    resource = get_resource(resource_id)
    if not resource:
        raise ResourceNotFoundError(resource_id)

    return {
        "data": resource.model_dump(),
        "support": {
            "url": "https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            "text": "Tired of writing endless social media content? Let Content Caddy generate it for you.",
        },
    }


@router.post("/api/unknown", status_code=201, tags=["Resources"])
def create_resource(resource_data: CreateResourceRequest) -> CreateResourceResponse:
    """Создать новый ресурс"""

    # Валидация данных
    if not resource_data.name or not resource_data.name.strip():
        raise ValidationError("Name is required")
    if resource_data.year < 1900 or resource_data.year > 2100:
        raise ValidationError("Invalid year")

    from app.database.resources import create_resource as db_create_resource

    try:
        # Сохраняем в БД
        db_resource = db_create_resource(
            name=resource_data.name,
            year=resource_data.year,
            color=resource_data.color,
            pantone_value=resource_data.pantone_value,
        )

        if not db_resource:
            raise ValidationError("Failed to create resource")

        # Возвращаем ответ в формате API
        created_at = datetime.now()
        return CreateResourceResponse(
            name=resource_data.name,
            year=resource_data.year,
            color=resource_data.color,
            pantone_value=resource_data.pantone_value,
            id=str(db_resource.id),
            createdAt=created_at,
        )

    except Exception as e:
        logger.error(f"Failed to create resource: {e}")
        raise ValidationError("Failed to create resource")


@router.put("/api/unknown/{resource_id}", tags=["Resources"])
def update_resource_put(
    resource_id: int, resource_data: UpdateResourceRequest
) -> UpdateResourceResponse:
    """Полное обновление ресурса"""

    # Валидация ID
    if resource_id < 1:
        raise InvalidIDError("resource ID")

    # Проверяем существование ресурса
    from app.database.resources import (
        get_resource,
        update_resource as db_update_resource,
    )

    existing_resource = get_resource(resource_id)
    if not existing_resource:
        raise ResourceNotFoundError(resource_id)

    try:
        # Обновляем ресурс в БД
        db_update_resource(
            resource_id=resource_id,
            name=resource_data.name,
            year=resource_data.year,
            color=resource_data.color,
            pantone_value=resource_data.pantone_value,
        )

        updated_at = datetime.now()
        return UpdateResourceResponse(
            name=resource_data.name,
            year=resource_data.year,
            color=resource_data.color,
            pantone_value=resource_data.pantone_value,
            updatedAt=updated_at,
        )

    except Exception as e:
        logger.error(f"Failed to update resource {resource_id}: {e}")
        raise ValidationError("Failed to update resource")


@router.patch("/api/unknown/{resource_id}", tags=["Resources"])
def update_resource_patch(
    resource_id: int, resource_data: UpdateResourceRequest
) -> UpdateResourceResponse:
    """Частичное обновление ресурса"""

    # Валидация ID
    if resource_id < 1:
        raise InvalidIDError("resource ID")

    # Проверяем существование ресурса
    from app.database.resources import (
        get_resource,
        update_resource as db_update_resource,
    )

    existing_resource = get_resource(resource_id)
    if not existing_resource:
        raise ResourceNotFoundError(resource_id)

    try:
        # Частичное обновление в БД
        db_update_resource(
            resource_id=resource_id,
            name=resource_data.name,
            year=resource_data.year,
            color=resource_data.color,
            pantone_value=resource_data.pantone_value,
        )

        updated_at = datetime.now()
        return UpdateResourceResponse(
            name=resource_data.name,
            year=resource_data.year,
            color=resource_data.color,
            pantone_value=resource_data.pantone_value,
            updatedAt=updated_at,
        )

    except Exception as e:
        logger.error(f"Failed to update resource {resource_id}: {e}")
        raise ValidationError("Failed to update resource")


@router.delete("/api/unknown/{resource_id}", status_code=204, tags=["Resources"])
def delete_resource(resource_id: int) -> None:
    """Удалить ресурс"""

    # Валидация ID
    if resource_id < 1:
        raise InvalidIDError("resource ID")

    from app.database.resources import delete_resource as db_delete_resource

    try:
        # Удаляем из БД
        deleted = db_delete_resource(resource_id)

        # Корректное поведение - 404 если ресурса не было
        if not deleted:
            raise ResourceNotFoundError(resource_id)

    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to delete resource {resource_id}: {e}")
        raise ValidationError("Failed to delete resource")
