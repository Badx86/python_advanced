from typing import Optional
from sqlmodel import Session, select, func
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page, Params
from app.database.engine import engine
from app.models import Resource
import logging

logger = logging.getLogger(__name__)


def get_resource(resource_id: int) -> Optional[Resource]:
    """Поиск ресурса по ID"""
    try:
        with Session(engine) as session:
            resource = session.get(Resource, resource_id)
            if resource:
                logger.debug(f"[DB] Found resource: {resource.name} ({resource.year})")
            else:
                logger.debug(f"[DB] Resource {resource_id} not found in database")
            return resource
    except Exception as e:
        logger.error(f"[DB] Error getting resource {resource_id}: {e}")
        return None


def get_resources_paginated(page: int = 1, size: int = 6) -> Page[Resource]:
    try:
        with Session(engine) as session:
            query = select(Resource).order_by(Resource.id)

            params = Params(page=page, size=size)
            result = paginate(session, query, params)

            logger.debug(
                f"[DB] Retrieved {len(result.items)} resources for page {page}"
            )
            return result

    except Exception as e:
        logger.error(f"[DB] Error getting resources page {page}: {e}")
        return Page(items=[], page=page, size=size, total=0, pages=0)


def create_resource(
    name: str, year: int, color: str, pantone_value: str
) -> Optional[Resource]:
    """Создать новый ресурс в БД"""
    try:
        with Session(engine) as session:
            new_resource = Resource(
                name=name, year=year, color=color, pantone_value=pantone_value
            )
            session.add(new_resource)
            session.commit()
            session.refresh(new_resource)

            logger.debug(
                f"[DB] Created resource: {new_resource.name} (ID: {new_resource.id})"
            )
            return new_resource
    except Exception as e:
        logger.error(f"[DB] Error creating resource: {e}")
        return None


def update_resource(
    resource_id: int,
    name: Optional[str] = None,
    year: Optional[int] = None,
    color: Optional[str] = None,
    pantone_value: Optional[str] = None,
) -> Optional[Resource]:
    """Обновить ресурс в БД"""
    try:
        with Session(engine) as session:
            resource: Optional[Resource] = session.get(Resource, resource_id)
            if not resource:
                logger.debug(f"[DB] Resource {resource_id} not found for update")
                return None

            # Обновляем только переданные поля
            if name is not None:
                resource.name = name
            if year is not None:
                resource.year = year
            if color is not None:
                resource.color = color
            if pantone_value is not None:
                resource.pantone_value = pantone_value

            session.add(resource)
            session.commit()
            session.refresh(resource)

            logger.debug(f"[DB] Updated resource {resource_id}: {resource.name}")
            return resource
    except Exception as e:
        logger.error(f"[DB] Error updating resource {resource_id}: {e}")
        return None


def delete_resource(resource_id: int) -> bool:
    """Удалить ресурс из БД"""
    try:
        with Session(engine) as session:
            resource = session.get(Resource, resource_id)
            if not resource:
                logger.debug(f"[DB] Resource {resource_id} not found for deletion")
                return False

            session.delete(resource)
            session.commit()

            logger.debug(f"[DB] Deleted resource {resource_id}: {resource.name}")
            return True
    except Exception as e:
        logger.error(f"[DB] Error deleting resource {resource_id}: {e}")
        return False


def get_resources_count() -> int:
    """Получить общее количество ресурсов"""
    try:
        with Session(engine) as session:
            count = session.exec(select(func.count(Resource.id))).one()
            return count
    except Exception as e:
        logger.error(f"[DB] Error getting resources count: {e}")
        return 0
