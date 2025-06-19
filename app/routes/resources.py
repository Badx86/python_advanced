from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import Session, select
from datetime import datetime
import logging

from app.database.engine import engine
from app.models import (
    Resource,
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    SingleResourceResponse,
    Support,
)
from app.exceptions import ResourceNotFoundError, ValidationError, InvalidIDError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/resources", tags=["Resources"])
def get_resources(params: Params = Depends()) -> Page[Resource]:
    """Получить список ресурсов с пагинацией"""

    # Работаем напрямую с БД
    with Session(engine) as session:
        query = select(Resource).order_by(Resource.id)
        return paginate(session, query, params)


@router.get("/api/resources/{resource_id}", tags=["Resources"])
def get_single_resource(resource_id: int) -> SingleResourceResponse:
    """Получить ресурс по ID"""

    # Валидация ID
    if resource_id < 1:
        raise InvalidIDError("resource ID")

    # Получаем ресурс из БД
    with Session(engine) as session:
        resource = session.get(Resource, resource_id)
        if not resource:
            raise ResourceNotFoundError(resource_id)

    return SingleResourceResponse(
        data=resource,
        support=Support(
            url="https://contentcaddy.io?utm_source=reqres&utm_medium=json&utm_campaign=referral",
            text="Tired of writing endless social media content? Let Content Caddy generate it for you.",
        ),
    )


@router.post("/api/resources", status_code=201, tags=["Resources"])
def create_resource(resource_data: ResourceCreate) -> ResourceResponse:
    """Создать новый ресурс"""

    # Валидация данных
    if not resource_data.name or not resource_data.name.strip():
        raise ValidationError("Name is required")
    if resource_data.year < 1900 or resource_data.year > 2100:
        raise ValidationError("Invalid year")

    try:
        # Сохраняем в БД напрямую
        with Session(engine) as session:
            db_resource = Resource(
                name=resource_data.name,
                year=resource_data.year,
                color=resource_data.color,
                pantone_value=resource_data.pantone_value,
            )

            session.add(db_resource)
            session.commit()
            session.refresh(db_resource)

        # Возвращаем ответ в формате API
        return ResourceResponse(
            name=resource_data.name,
            year=resource_data.year,
            color=resource_data.color,
            pantone_value=resource_data.pantone_value,
            id=str(db_resource.id),
            createdAt=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Failed to create resource: {e}")
        raise ValidationError("Failed to create resource")


@router.put("/api/resources/{resource_id}", tags=["Resources"])
def update_resource_put(
    resource_id: int, resource_data: ResourceUpdate
) -> ResourceResponse:
    """Полное обновление ресурса"""

    # Валидация ID
    if resource_id < 1:
        raise InvalidIDError("resource ID")

    try:
        with Session(engine) as session:
            # Проверяем существование ресурса
            resource = session.get(Resource, resource_id)
            if not resource:
                raise ResourceNotFoundError(resource_id)

            # Обновляем ресурс в БД
            if resource_data.name is not None:
                resource.name = resource_data.name
            if resource_data.year is not None:
                resource.year = resource_data.year
            if resource_data.color is not None:
                resource.color = resource_data.color
            if resource_data.pantone_value is not None:
                resource.pantone_value = resource_data.pantone_value

            session.add(resource)
            session.commit()
            session.refresh(resource)

        return ResourceResponse(
            name=resource_data.name or resource.name,
            year=resource_data.year or resource.year,
            color=resource_data.color or resource.color,
            pantone_value=resource_data.pantone_value or resource.pantone_value,
            id=str(resource.id),
            updatedAt=datetime.now(),
        )

    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to update resource {resource_id}: {e}")
        raise ValidationError("Failed to update resource")


@router.patch("/api/resources/{resource_id}", tags=["Resources"])
def update_resource_patch(
    resource_id: int, resource_data: ResourceUpdate
) -> ResourceResponse:
    """Частичное обновление ресурса"""

    # Валидация ID
    if resource_id < 1:
        raise InvalidIDError("resource ID")

    try:
        with Session(engine) as session:
            # Проверяем существование ресурса
            resource = session.get(Resource, resource_id)
            if not resource:
                raise ResourceNotFoundError(resource_id)

            # Частичное обновление в БД
            if resource_data.name is not None:
                resource.name = resource_data.name
            if resource_data.year is not None:
                resource.year = resource_data.year
            if resource_data.color is not None:
                resource.color = resource_data.color
            if resource_data.pantone_value is not None:
                resource.pantone_value = resource_data.pantone_value

            session.add(resource)
            session.commit()
            session.refresh(resource)

        return ResourceResponse(
            name=resource_data.name or resource.name,
            year=resource_data.year or resource.year,
            color=resource_data.color or resource.color,
            pantone_value=resource_data.pantone_value or resource.pantone_value,
            id=str(resource.id),
            updatedAt=datetime.now(),
        )

    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to update resource {resource_id}: {e}")
        raise ValidationError("Failed to update resource")


@router.delete("/api/resources/{resource_id}", status_code=204, tags=["Resources"])
def delete_resource(resource_id: int) -> None:
    """Удалить ресурс"""

    # Валидация ID
    if resource_id < 1:
        raise InvalidIDError("resource ID")

    try:
        with Session(engine) as session:
            resource = session.get(Resource, resource_id)
            if not resource:
                raise ResourceNotFoundError(resource_id)

            session.delete(resource)
            session.commit()

    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to delete resource {resource_id}: {e}")
        raise ValidationError("Failed to delete resource")
