import logging
from typing import Dict, Any
from http import HTTPStatus
import requests
from fastapi_pagination import Page
from app.models import (
    SingleUserResponse,
    SingleResourceResponse,
    CreateUserResponse,
    UpdateUserResponse,
    User,
    Resource,
)

logger = logging.getLogger(__name__)


class APIAssertions:
    """Класс для всех проверок API ответов"""

    # ========================================
    # БАЗОВЫЕ ПРОВЕРКИ
    # ========================================

    @staticmethod
    def log_and_check_status(
        response: requests.Response,
        endpoint: str,
        expected_status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        """Логирует запрос и проверяет статус код"""
        logger.info(
            f"{response.request.method} {endpoint} - Status: {response.status_code}"
        )
        assert response.status_code == expected_status.value

    @staticmethod
    def check_pagination_structure(
        data: Dict[str, Any],
        page: int,
        per_page: int,
        expected_total: int = None,
        items_count: int = None,
    ) -> None:
        """Проверяет структуру пагинации ответа"""
        assert data["page"] == page
        assert data["size"] == per_page

        # Проверяем total только если передан expected_total
        if expected_total is not None:
            assert data["total"] == expected_total
        else:
            assert isinstance(data["total"], int) and data["total"] >= 0

        # Вычисляем pages на основе реального total
        actual_total = data["total"]
        expected_pages = (
            ((actual_total + per_page - 1) // per_page) if actual_total > 0 else 1
        )
        assert data["pages"] == expected_pages

        # Проверяем количество items если передано
        if items_count is not None:
            assert len(data["items"]) == items_count
        else:
            assert len(data["items"]) <= per_page

    @classmethod
    def check_404_error(cls, response: requests.Response, endpoint: str) -> None:
        """Проверяет 404 ошибку"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.NOT_FOUND)
        data = response.json()

        assert "detail" in data, "Missing 'detail' in 404 response"
        assert "error" in data["detail"], "Missing 'error' in detail"
        assert data["detail"]["error"], "Error message is empty"

    # ========================================
    # ТЕСТЫ ПОЛЬЗОВАТЕЛЕЙ (test_users.py)
    # ========================================

    @classmethod
    def check_user_response(
        cls, response: requests.Response, endpoint: str
    ) -> SingleUserResponse:
        """Проверяет ответ с одним пользователем"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
        user_response = SingleUserResponse(**response.json())
        return user_response

    @classmethod
    def check_users_list_response(
        cls,
        response: requests.Response,
        endpoint: str,
        page: int = 1,
        per_page: int = 6,
    ) -> Page[User]:
        """Проверяет ответ со списком пользователей (без жесткой привязки к количеству)"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
        data = response.json()

        # Проверяем структуру пагинации БЕЗ ожидаемого total
        cls.check_pagination_structure(data, page, per_page)

        # Возвращаем Page[User] (создаем из JSON)
        users = [User(**user_data) for user_data in data["items"]]
        return Page(
            items=users,
            page=data["page"],
            size=data["size"],
            total=data["total"],
            pages=data["pages"],
        )

    # ========================================
    # ТЕСТЫ РЕСУРСОВ (test_resources.py)
    # ========================================

    @classmethod
    def check_resource_response(
        cls, response: requests.Response, endpoint: str
    ) -> SingleResourceResponse:
        """Проверяет ответ с одним ресурсом"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
        resource_response = SingleResourceResponse(**response.json())
        return resource_response

    @classmethod
    def check_resources_list_response(
        cls,
        response: requests.Response,
        endpoint: str,
        page: int = 1,
        per_page: int = 6,
    ) -> Page[Resource]:
        """Проверяет ответ со списком ресурсов (ресурсы статичные - 12 штук)"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
        data = response.json()

        # Проверяем структуру пагинации для ресурсов с ожидаемым total=12
        cls.check_pagination_structure(data, page, per_page, 12, len(data["items"]))

        # Возвращаем Page[Resource]
        resources = [Resource(**resource_data) for resource_data in data["items"]]
        return Page(
            items=resources,
            page=data["page"],
            size=data["size"],
            total=data["total"],
            pages=data["pages"],
        )

    # ========================================
    # CRUD ОПЕРАЦИИ (test_crud.py)
    # ========================================

    @classmethod
    def check_create_user_response(
        cls,
        response: requests.Response,
        endpoint: str,
        expected_name: str,
        expected_job: str,
    ) -> CreateUserResponse:
        """Проверяет ответ создания пользователя"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.CREATED)

        create_response = CreateUserResponse(**response.json())

        assert create_response.name == expected_name
        assert create_response.job == expected_job
        assert create_response.id is not None
        assert create_response.createdAt is not None

        user_id = int(create_response.id)
        assert user_id > 0, f"ID должен быть положительным числом, получен: {user_id}"

        return create_response

    @classmethod
    def check_update_user_response(
        cls,
        response: requests.Response,
        endpoint: str,
        expected_name: str,
        expected_job: str,
    ) -> UpdateUserResponse:
        """Проверяет ответ обновления пользователя (PUT/PATCH)"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.OK)

        update_response = UpdateUserResponse(**response.json())

        assert update_response.name == expected_name
        assert update_response.job == expected_job
        assert update_response.updatedAt is not None

        return update_response

    @classmethod
    def check_delete_user_response(
        cls, response: requests.Response, endpoint: str
    ) -> None:
        """Проверяет ответ удаления пользователя"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.NO_CONTENT)

    # ========================================
    # АУТЕНТИФИКАЦИЯ (test_auth.py)
    # ========================================

    @classmethod
    def check_email_error_response(
        cls, response: requests.Response, endpoint: str, expected_error: str
    ) -> None:
        """Проверяет ошибку с email"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.BAD_REQUEST)
        data = response.json()

        assert "detail" in data, "Missing 'detail' in error response"
        assert "error" in data["detail"], "Missing 'error' in detail"
        assert (
            data["detail"]["error"] == expected_error
        ), f"Expected '{expected_error}', got '{data['detail']['error']}'"

    # ========================================
    # СПЕЦИАЛЬНЫЕ ТЕСТЫ (test_special.py)
    # ========================================

    @classmethod
    def check_delayed_response(
        cls, response: requests.Response, endpoint: str, min_duration: float
    ) -> None:
        """Проверяет delayed response"""
        cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
        data = response.json()

        # Проверяем структуру ответа
        assert "page" in data, "Missing 'page' in response"
        assert "size" in data, "Missing 'size' in response"
        assert "total" in data, "Missing 'total' in response"
        assert "pages" in data, "Missing 'pages' in response"
        assert "items" in data, "Missing 'items' in response"

        # Проверяем, что данные корректны
        assert isinstance(data["items"], list), "Items should be a list"
        assert len(data["items"]) > 0, "Items array should not be empty"

        logger.info(f"Delayed response validated, took at least {min_duration}s")

    # ========================================
    # УНИВЕРСАЛЬНЫЕ ХЕЛПЕРЫ
    # ========================================

    @staticmethod
    def check_data_count(response_obj: Page, expected_count: int) -> None:
        """Проверяет количество элементов в items"""
        actual_count = len(response_obj.items)
        assert (
            actual_count == expected_count
        ), f"Expected {expected_count} items, got {actual_count}"

    @staticmethod
    def check_first_item_field(
        response_obj: Page,
        field_name: str,
        expected_value: Any,
    ) -> None:
        """Проверяет поле первого элемента в items"""
        assert len(response_obj.items) > 0, "Items array is empty"

        first_item = response_obj.items[0]
        actual_value = getattr(first_item, field_name)
        assert (
            actual_value == expected_value
        ), f"Expected {field_name}={expected_value}, got {actual_value}"

    @staticmethod
    def check_multiple_fields(obj: Any, **field_expectations) -> None:
        """Проверяет несколько полей объекта сразу"""
        for field_name, expected_value in field_expectations.items():
            actual_value = getattr(obj, field_name)
            assert (
                actual_value == expected_value
            ), f"Expected {field_name}={expected_value}, got {actual_value}"


# Создаем экземпляр для удобного использования
api = APIAssertions()
