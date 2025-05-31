import logging
from typing import Dict, Any
import requests
from app.models import (
    UsersListResponse,
    SingleUserResponse,
    ResourcesListResponse,
    SingleResourceResponse,
)

logger = logging.getLogger(__name__)


def log_and_assert_status(
    response: requests.Response, endpoint: str, expected_status: int = 200
) -> None:
    """Логирует запрос и проверяет статус код"""
    logger.info(
        f"{response.request.method} {endpoint} - Status: {response.status_code}"
    )
    assert response.status_code == expected_status


def assert_list_structure(
    data: Dict[str, Any], page: int, per_page: int, total: int, data_count: int
) -> None:
    """Проверяет базовую структуру списочного ответа"""
    assert data["page"] == page
    assert data["per_page"] == per_page
    assert data["total"] == total
    assert data["total_pages"] == (total + per_page - 1) // per_page  # math.ceil
    assert len(data["data"]) == data_count


def assert_support_block(data: Dict[str, Any]) -> None:
    """Проверяет блок support"""
    assert "support" in data
    assert "url" in data["support"]
    assert "text" in data["support"]
    assert "contentcaddy.io" in data["support"]["url"]


def assert_404_error(response: requests.Response, endpoint: str) -> None:
    """Проверяет 404 ошибку"""
    log_and_assert_status(response, endpoint, 404)
    data = response.json()
    assert data["detail"] == {}


def assert_user_response(
    response: requests.Response, endpoint: str
) -> SingleUserResponse:
    """Проверяет ответ с одним пользователем и возвращает типизированный объект"""
    log_and_assert_status(response, endpoint)
    user_response = SingleUserResponse(**response.json())
    assert_support_block(response.json())
    return user_response


def assert_users_list_response(
    response: requests.Response, endpoint: str, page: int = 1, per_page: int = 6
) -> UsersListResponse:
    """Проверяет ответ со списком пользователей и возвращает типизированный объект"""
    log_and_assert_status(response, endpoint)
    data = response.json()

    assert_list_structure(data, page, per_page, 12, len(data["data"]))
    assert_support_block(data)

    users_response = UsersListResponse(**data)
    return users_response


def assert_resource_response(
    response: requests.Response, endpoint: str
) -> SingleResourceResponse:
    """Проверяет ответ с одним ресурсом и возвращает типизированный объект"""
    log_and_assert_status(response, endpoint)
    resource_response = SingleResourceResponse(**response.json())
    assert_support_block(response.json())
    return resource_response


def assert_resources_list_response(
    response: requests.Response, endpoint: str, page: int = 1, per_page: int = 6
) -> ResourcesListResponse:
    """Проверяет ответ со списком ресурсов и возвращает типизированный объект"""
    log_and_assert_status(response, endpoint)
    data = response.json()

    assert_list_structure(data, page, per_page, 12, len(data["data"]))
    assert_support_block(data)

    resources_response = ResourcesListResponse(**data)
    return resources_response


def assert_user_fields(
    user_data: Dict[str, Any],
    expected_id: int,
    expected_email: str,
    expected_first_name: str,
    expected_last_name: str,
) -> None:
    """Проверяет поля конкретного пользователя"""
    assert user_data["id"] == expected_id
    assert user_data["email"] == expected_email
    assert user_data["first_name"] == expected_first_name
    assert user_data["last_name"] == expected_last_name


def assert_resource_fields(
    resource_data: Dict[str, Any],
    expected_id: int,
    expected_name: str,
    expected_year: int,
    expected_color: str,
    expected_pantone: str,
) -> None:
    """Проверяет поля конкретного ресурса"""
    assert resource_data["id"] == expected_id
    assert resource_data["name"] == expected_name
    assert resource_data["year"] == expected_year
    assert resource_data["color"] == expected_color
    assert resource_data["pantone_value"] == expected_pantone
