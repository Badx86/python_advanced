import logging
from typing import Dict, Any
import requests
from app.models import (
    UsersListResponse,
    SingleUserResponse,
    ResourcesListResponse,
    SingleResourceResponse,
    CreateUserResponse,
    UpdateUserResponse,
)

logger = logging.getLogger(__name__)


class APIAssertions:
    """Класс для всех проверок API ответов"""

    @staticmethod
    def log_and_check_status(
        response: requests.Response, endpoint: str, expected_status: int = 200
    ) -> None:
        """Логирует запрос и проверяет статус код"""
        logger.info(
            f"{response.request.method} {endpoint} - Status: {response.status_code}"
        )
        assert response.status_code == expected_status

    @staticmethod
    def check_list_structure(
        data: Dict[str, Any], page: int, per_page: int, total: int, data_count: int
    ) -> None:
        """Проверяет базовую структуру списочного ответа"""
        assert data["page"] == page
        assert data["per_page"] == per_page
        assert data["total"] == total
        assert data["total_pages"] == (total + per_page - 1) // per_page  # math.ceil
        assert len(data["data"]) == data_count

    @staticmethod
    def check_support_block(data: Dict[str, Any]) -> None:
        """Проверяет блок support"""
        assert "support" in data
        assert "url" in data["support"]
        assert "text" in data["support"]
        assert "contentcaddy.io" in data["support"]["url"]

    @classmethod
    def check_404_error(cls, response: requests.Response, endpoint: str) -> None:
        """Проверяет 404 ошибку"""
        cls.log_and_check_status(response, endpoint, 404)
        data = response.json()
        assert data["detail"] == {}

    @classmethod
    def check_user_response(
        cls, response: requests.Response, endpoint: str
    ) -> SingleUserResponse:
        """Проверяет ответ с одним пользователем и возвращает типизированный объект"""
        cls.log_and_check_status(response, endpoint)
        user_response = SingleUserResponse(**response.json())
        cls.check_support_block(response.json())
        return user_response

    @classmethod
    def check_users_list_response(
        cls,
        response: requests.Response,
        endpoint: str,
        page: int = 1,
        per_page: int = 6,
    ) -> UsersListResponse:
        """Проверяет ответ со списком пользователей и возвращает типизированный объект"""
        cls.log_and_check_status(response, endpoint)
        data = response.json()

        cls.check_list_structure(data, page, per_page, 12, len(data["data"]))
        cls.check_support_block(data)

        users_response = UsersListResponse(**data)
        return users_response

    @classmethod
    def check_resource_response(
        cls, response: requests.Response, endpoint: str
    ) -> SingleResourceResponse:
        """Проверяет ответ с одним ресурсом и возвращает типизированный объект"""
        cls.log_and_check_status(response, endpoint)
        resource_response = SingleResourceResponse(**response.json())
        cls.check_support_block(response.json())
        return resource_response

    @classmethod
    def check_resources_list_response(
        cls,
        response: requests.Response,
        endpoint: str,
        page: int = 1,
        per_page: int = 6,
    ) -> ResourcesListResponse:
        """Проверяет ответ со списком ресурсов и возвращает типизированный объект"""
        cls.log_and_check_status(response, endpoint)
        data = response.json()

        cls.check_list_structure(data, page, per_page, 12, len(data["data"]))
        cls.check_support_block(data)

        resources_response = ResourcesListResponse(**data)
        return resources_response

    # CRUD операции
    @classmethod
    def check_create_user_response(
        cls,
        response: requests.Response,
        endpoint: str,
        expected_name: str,
        expected_job: str,
    ) -> CreateUserResponse:
        """Проверяет ответ создания пользователя"""
        cls.log_and_check_status(response, endpoint, 201)

        create_response = CreateUserResponse(**response.json())

        assert create_response.name == expected_name
        assert create_response.job == expected_job
        assert create_response.id is not None
        assert create_response.createdAt is not None

        # Проверяем диапазон ID как в reqres.in
        user_id = int(create_response.id)
        assert (
            500 <= user_id <= 999
        ), f"ID должен быть в диапазоне 500-999, получен: {user_id}"

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
        cls.log_and_check_status(response, endpoint, 200)

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
        cls.log_and_check_status(response, endpoint, 204)
        # Тело ответа должно быть пустым при 204

    # Универсальные проверки данных
    @staticmethod
    def check_data_count(
        response_obj: Any, expected_count: int, data_field: str = "data"
    ) -> None:
        """Проверяет количество элементов в массиве данных"""
        data = getattr(response_obj, data_field)
        actual_count = len(data)
        assert (
            actual_count == expected_count
        ), f"Expected {expected_count} items, got {actual_count}"

    @staticmethod
    def check_first_item_field(
        response_obj: Any,
        field_name: str,
        expected_value: Any,
        data_field: str = "data",
    ) -> None:
        """Проверяет поле первого элемента в массиве данных"""
        data = getattr(response_obj, data_field)
        assert len(data) > 0, "Data array is empty"

        first_item = data[0]
        actual_value = getattr(first_item, field_name)
        assert (
            actual_value == expected_value
        ), f"Expected {field_name}={expected_value}, got {actual_value}"

    @staticmethod
    def check_item_field(
        response_obj: Any,
        index: int,
        field_name: str,
        expected_value: Any,
        data_field: str = "data",
    ) -> None:
        """Проверяет поле элемента по индексу в массиве данных"""
        data = getattr(response_obj, data_field)
        assert (
            len(data) > index
        ), f"Data array has only {len(data)} items, cannot access index {index}"

        item = data[index]
        actual_value = getattr(item, field_name)
        assert (
            actual_value == expected_value
        ), f"Expected data[{index}].{field_name}={expected_value}, got {actual_value}"

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
