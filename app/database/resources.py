from typing import Iterable, Optional
from sqlmodel import Session, select, func
from fastapi_pagination import Page
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
                logger.info(f"Found resource: {resource.name} ({resource.year})")
            else:
                logger.warning(f"Resource {resource_id} not found in database")
            return resource
    except Exception as e:
        logger.error(f"Error getting resource {resource_id}: {e}")
        return None


def get_resources_paginated(page: int = 1, size: int = 6) -> Page[Resource]:
    """Получить список ресурсов с пагинацией"""
    try:
        with Session(engine) as session:
            # Подсчет общего количества ресурсов
            total_count = session.exec(select(func.count(Resource.id))).one()

            # Получение ресурсов для текущей страницы
            offset = (page - 1) * size
            statement = select(Resource).offset(offset).limit(size)
            resources = session.exec(statement).all()

            # Подсчет общего количества страниц
            total_pages = (total_count + size - 1) // size

            logger.info(f"Retrieved {len(resources)} resources for page {page}")

            return Page(
                items=resources,
                page=page,
                size=size,
                total=total_count,
                pages=total_pages,
            )
    except Exception as e:
        logger.error(f"Error getting resources page {page}: {e}")
        # Возвращаем пустую страницу в случае ошибки
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

            logger.info(
                f"Created resource: {new_resource.name} (ID: {new_resource.id})"
            )
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
                logger.warning(f"Resource {resource_id} not found for update")
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

            logger.info(f"Updated resource {resource_id}: {resource.name}")
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
                logger.warning(f"Resource {resource_id} not found for deletion")
                return False

            session.delete(resource)
            session.commit()

            logger.info(f"Deleted resource {resource_id}: {resource.name}")
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
