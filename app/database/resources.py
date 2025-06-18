from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page
from sqlmodel import Session, select, func
from app.database.engine import engine
from app.models import Resource
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_resource(resource_id: int) -> Optional[Resource]:
    """Поиск ресурса по ID"""
    try:
        with Session(engine) as session:
            resource = session.get(Resource, resource_id)
            return resource
    except Exception as e:
        logger.error(f"Error getting resource {resource_id}: {e}")
        return None


def get_resources_paginated(session: Session) -> Page[Resource]:
    """Получить список ресурсов с пагинацией"""
    try:
        query = select(Resource).order_by(Resource.id)
        result = paginate(session, query)
        return result

    except Exception as e:
        logger.error(f"Error getting resources: {e}")
        return Page(items=[], page=1, size=6, total=0, pages=0)


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
            return new_resource
    except Exception as e:
        logger.error(f"Error creating resource: {e}")
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
            return resource
    except Exception as e:
        logger.error(f"Error updating resource {resource_id}: {e}")
        return None


def delete_resource(resource_id: int) -> bool:
    """Удалить ресурс из БД"""
    try:
        with Session(engine) as session:
            resource = session.get(Resource, resource_id)
            if not resource:
                return False

            session.delete(resource)
            session.commit()
            return True
    except Exception as e:
        logger.error(f"Error deleting resource {resource_id}: {e}")
        return False


def get_resources_count() -> int:
    """Получить общее количество ресурсов"""
    try:
        with Session(engine) as session:
            count = session.exec(select(func.count(Resource.id))).one()
            return count
    except Exception as e:
        logger.error(f"Error getting resources count: {e}")
        return 0
