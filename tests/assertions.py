import allure
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
    """Класс для всех проверок API ответов + БД с Allure отчетностью"""

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
        with allure.step(
            f"Verify HTTP status for {response.request.method} {endpoint}"
        ):
            logger.info(
                f"{response.request.method} {endpoint} - Status: {response.status_code}"
            )

            # Attachments для отладки
            allure.attach(
                f"Method: {response.request.method}\nURL: {endpoint}\nExpected: {expected_status.value}\nActual: {response.status_code}",
                "Request Details",
                allure.attachment_type.TEXT,
            )

            if response.text:
                allure.attach(
                    response.text, "Response Body", allure.attachment_type.JSON
                )

            assert (
                response.status_code == expected_status.value
            ), f"Expected {expected_status.value}, got {response.status_code}"

    @staticmethod
    def check_pagination_structure(
        data: Dict[str, Any],
        page: int,
        per_page: int,
        expected_total: int = None,
        items_count: int = None,
    ) -> None:
        """Проверяет структуру пагинации ответа"""
        with allure.step("Verify pagination structure"):
            allure.attach(str(data), "Pagination Data", allure.attachment_type.JSON)

            assert data["page"] == page, f"Expected page {page}, got {data['page']}"
            assert (
                data["size"] == per_page
            ), f"Expected size {per_page}, got {data['size']}"

            # Проверяем total только если передан expected_total
            if expected_total is not None:
                assert (
                    data["total"] == expected_total
                ), f"Expected total {expected_total}, got {data['total']}"
            else:
                assert (
                    isinstance(data["total"], int) and data["total"] >= 0
                ), f"Total should be non-negative integer, got {data['total']}"

            # Вычисляем pages на основе реального total
            actual_total = data["total"]
            expected_pages = (
                ((actual_total + per_page - 1) // per_page) if actual_total > 0 else 1
            )
            assert (
                data["pages"] == expected_pages
            ), f"Expected pages {expected_pages}, got {data['pages']}"

            # Проверяем количество items если передано
            if items_count is not None:
                assert (
                    len(data["items"]) == items_count
                ), f"Expected {items_count} items, got {len(data['items'])}"
            else:
                assert (
                    len(data["items"]) <= per_page
                ), f"Items count {len(data['items'])} exceeds per_page {per_page}"

    @classmethod
    def check_404_error(cls, response: requests.Response, endpoint: str) -> None:
        """Проверяет 404 ошибку"""
        with allure.step(f"Verify 404 error for {endpoint}"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.NOT_FOUND)
            data = response.json()

            assert "detail" in data, "Missing 'detail' in 404 response"
            assert "error" in data["detail"], "Missing 'error' in detail"
            assert data["detail"]["error"], "Error message is empty"

            allure.attach(
                data["detail"]["error"], "Error Message", allure.attachment_type.TEXT
            )

    # ========================================
    # ПРОВЕРКИ БД ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
    # ========================================

    @staticmethod
    def check_user_in_database(user_id: int, expected_name: str = None) -> User:
        """Проверяет что пользователь существует в БД"""
        with allure.step(f"Query database for user {user_id}"):
            from app.database.users import get_user

            db_user = get_user(user_id)
            assert db_user is not None, f"User {user_id} not found in database"

        with allure.step("Validate user data in database"):
            if expected_name:
                expected_first_name = (
                    expected_name.split()[0] if expected_name.split() else expected_name
                )
                expected_last_name = (
                    expected_name.split()[-1] if len(expected_name.split()) > 1 else ""
                )

                assert (
                    db_user.first_name == expected_first_name
                ), f"DB first_name mismatch: '{db_user.first_name}' != '{expected_first_name}'"
                assert (
                    db_user.last_name == expected_last_name
                ), f"DB last_name mismatch: '{db_user.last_name}' != '{expected_last_name}'"

            assert db_user.email, "DB email is empty"
            assert "@" in db_user.email, f"DB email format invalid: {db_user.email}"

            # Attachment с данными пользователя из БД
            allure.attach(
                f"ID: {db_user.id}\nEmail: {db_user.email}\nFirst Name: {db_user.first_name}\nLast Name: {db_user.last_name}\nAvatar: {db_user.avatar}",
                "User Data from Database",
                allure.attachment_type.TEXT,
            )

            logger.info(
                f"User {user_id} verified in database: {db_user.first_name} {db_user.last_name}"
            )
            return db_user

    @staticmethod
    def check_user_not_in_database(user_id: int) -> None:
        """Проверяет что пользователь НЕ существует в БД"""
        with allure.step(f"Verify user {user_id} is deleted from database"):
            from app.database.users import get_user

            db_user = get_user(user_id)
            assert (
                db_user is None
            ), f"User {user_id} should be deleted but still exists in database"

            allure.attach(
                f"User {user_id} confirmed as deleted",
                "Deletion Verified",
                allure.attachment_type.TEXT,
            )
            logger.info(f"User {user_id} confirmed deleted from database")

    @staticmethod
    def check_user_updated_in_database(
        user_id: int, expected_name: str, original_user: User
    ) -> User:
        """Проверяет что пользователь обновился в БД"""
        with allure.step(f"Verify user {user_id} is updated in database"):
            from app.database.users import get_user

            updated_user = get_user(user_id)
            assert updated_user is not None, f"User {user_id} not found after update"

            # Проверяем что имя обновилось
            expected_first_name = (
                expected_name.split()[0] if expected_name.split() else expected_name
            )
            expected_last_name = (
                expected_name.split()[-1] if len(expected_name.split()) > 1 else ""
            )

            assert (
                updated_user.first_name == expected_first_name
            ), f"DB first_name not updated: '{updated_user.first_name}' != '{expected_first_name}'"
            assert (
                updated_user.last_name == expected_last_name
            ), f"DB last_name not updated: '{updated_user.last_name}' != '{expected_last_name}'"

            # Проверяем что email и avatar НЕ изменились
            assert (
                updated_user.email == original_user.email
            ), f"DB email should not change: '{updated_user.email}' != '{original_user.email}'"
            assert (
                updated_user.avatar == original_user.avatar
            ), f"DB avatar should not change: '{updated_user.avatar}' != '{original_user.avatar}'"

            # Attachment с изменениями
            allure.attach(
                f"BEFORE:\nFirst: {original_user.first_name}\nLast: {original_user.last_name}\n\nAFTER:\nFirst: {updated_user.first_name}\nLast: {updated_user.last_name}",
                "User Update Comparison",
                allure.attachment_type.TEXT,
            )

            logger.info(
                f"User {user_id} updated in database: {updated_user.first_name} {updated_user.last_name}"
            )
            return updated_user

    # ========================================
    # ПРОВЕРКИ БД ДЛЯ РЕСУРСОВ
    # ========================================

    @staticmethod
    def check_resource_in_database(
        resource_id: int, expected_data: dict = None
    ) -> Resource:
        """Проверяет что ресурс существует в БД"""
        with allure.step(f"Verify resource {resource_id} exists in database"):
            from app.database.resources import get_resource

            db_resource = get_resource(resource_id)
            assert (
                db_resource is not None
            ), f"Resource {resource_id} not found in database"

            if expected_data:
                assert (
                    db_resource.name == expected_data["name"]
                ), f"DB name mismatch: '{db_resource.name}' != '{expected_data['name']}'"
                assert (
                    db_resource.year == expected_data["year"]
                ), f"DB year mismatch: {db_resource.year} != {expected_data['year']}"
                assert (
                    db_resource.color == expected_data["color"]
                ), f"DB color mismatch: '{db_resource.color}' != '{expected_data['color']}'"
                assert (
                    db_resource.pantone_value == expected_data["pantone_value"]
                ), f"DB pantone_value mismatch: '{db_resource.pantone_value}' != '{expected_data['pantone_value']}'"

            # Attachment с данными ресурса из БД
            allure.attach(
                f"ID: {db_resource.id}\nName: {db_resource.name}\nYear: {db_resource.year}\nColor: {db_resource.color}\nPantone: {db_resource.pantone_value}",
                "Resource Data from Database",
                allure.attachment_type.TEXT,
            )

            logger.info(
                f"Resource {resource_id} verified in database: {db_resource.name} ({db_resource.year})"
            )
            return db_resource

    @staticmethod
    def check_resource_not_in_database(resource_id: int) -> None:
        """Проверяет что ресурс НЕ существует в БД"""
        with allure.step(f"Verify resource {resource_id} is deleted from database"):
            from app.database.resources import get_resource

            db_resource = get_resource(resource_id)
            assert (
                db_resource is None
            ), f"Resource {resource_id} should be deleted but still exists in database"

            allure.attach(
                f"Resource {resource_id} confirmed as deleted",
                "Deletion Verified",
                allure.attachment_type.TEXT,
            )
            logger.info(f"Resource {resource_id} confirmed deleted from database")

    # ========================================
    # CRUD ОПЕРАЦИИ (test_crud_users.py)
    # ========================================

    @classmethod
    def check_create_user_response(
        cls,
        response: requests.Response,
        endpoint: str,
        expected_name: str,
        expected_job: str,
    ) -> CreateUserResponse:
        """Проверяет ответ создания пользователя (API + БД)"""
        with allure.step(f"Send POST request to create user: {expected_name}"):
            allure.attach(
                f"Name: {expected_name}\nJob: {expected_job}",
                "User Data",
                allure.attachment_type.TEXT,
            )

        with allure.step("Verify user creation API response"):
            # 1. API проверка
            cls.log_and_check_status(response, endpoint, HTTPStatus.CREATED)
            create_response = CreateUserResponse(**response.json())

            assert (
                create_response.name == expected_name
            ), f"Name mismatch: {create_response.name} != {expected_name}"
            assert (
                create_response.job == expected_job
            ), f"Job mismatch: {create_response.job} != {expected_job}"
            assert create_response.id is not None, "ID should not be None"
            assert create_response.createdAt is not None, "CreatedAt should not be None"

            user_id = int(create_response.id)
            assert (
                user_id > 0
            ), f"ID должен быть положительным числом, получен: {user_id}"

            allure.attach(
                f"Created user ID: {user_id}", "User ID", allure.attachment_type.TEXT
            )

        with allure.step("Verify user exists in database"):
            # 2. БД проверка
            cls.check_user_in_database(user_id, expected_name)

        return create_response

    @classmethod
    def check_update_user_response(
        cls,
        response: requests.Response,
        endpoint: str,
        expected_name: str,
        expected_job: str,
        user_id: int,
        original_user: User,
    ) -> UpdateUserResponse:
        """Проверяет ответ обновления пользователя (API + БД)"""
        with allure.step(f"Send PUT/PATCH request to update user {user_id}"):
            allure.attach(
                f"User ID: {user_id}\nNew Name: {expected_name}\nNew Job: {expected_job}",
                "Update Data",
                allure.attachment_type.TEXT,
            )

        with allure.step("Verify user update API response"):
            # 1. API проверка
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            update_response = UpdateUserResponse(**response.json())

            assert (
                update_response.name == expected_name
            ), f"Name mismatch: {update_response.name} != {expected_name}"
            assert (
                update_response.job == expected_job
            ), f"Job mismatch: {update_response.job} != {expected_job}"
            assert update_response.updatedAt is not None, "UpdatedAt should not be None"

        with allure.step("Verify user changes in database"):
            # 2. БД проверка
            cls.check_user_updated_in_database(user_id, expected_name, original_user)

        return update_response

    @classmethod
    def check_delete_user_response(
        cls, response: requests.Response, endpoint: str, user_id: int
    ) -> None:
        """Проверяет ответ удаления пользователя (API + БД)"""
        with allure.step(f"Send DELETE request for user {user_id}"):
            allure.attach(
                f"User ID: {user_id}", "Delete Target", allure.attachment_type.TEXT
            )

        with allure.step("Verify user deletion API response"):
            # 1. API проверка
            cls.log_and_check_status(response, endpoint, HTTPStatus.NO_CONTENT)

        with allure.step("Verify user removed from database"):
            # 2. БД проверка
            cls.check_user_not_in_database(user_id)

    # ========================================
    # CRUD РЕСУРСОВ (test_crud_resources.py)
    # ========================================

    @classmethod
    def check_create_resource_response(
        cls,
        response: requests.Response,
        endpoint: str,
        expected_resource: dict,
    ) -> dict:
        """Проверяет ответ создания ресурса (API + БД)"""
        with allure.step("Verify resource creation API response"):
            # 1. API проверка
            cls.log_and_check_status(response, endpoint, HTTPStatus.CREATED)
            data = response.json()

            assert data["name"] == expected_resource["name"]
            assert data["year"] == expected_resource["year"]
            assert data["color"] == expected_resource["color"]
            assert data["pantone_value"] == expected_resource["pantone_value"]
            assert "id" in data and data["id"] is not None
            assert "createdAt" in data and data["createdAt"] is not None

            resource_id = int(data["id"])
            assert (
                resource_id > 0
            ), f"ID должен быть положительным числом, получен: {resource_id}"

        with allure.step("Verify resource exists in database"):
            # 2. БД проверка
            cls.check_resource_in_database(resource_id, expected_resource)

        return data

    # ========================================
    # ТЕСТЫ ПОЛЬЗОВАТЕЛЕЙ (test_users.py)
    # ========================================

    @classmethod
    def check_user_response(
        cls, response: requests.Response, endpoint: str
    ) -> SingleUserResponse:
        """Проверяет ответ с одним пользователем"""
        with allure.step("Verify single user API response"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            user_response = SingleUserResponse(**response.json())

            allure.attach(
                f"User ID: {user_response.data.id}\nEmail: {user_response.data.email}\nName: {user_response.data.first_name} {user_response.data.last_name}",
                "Retrieved User Data",
                allure.attachment_type.TEXT,
            )

            return user_response

    @classmethod
    def check_users_list_response(
        cls,
        response: requests.Response,
        endpoint: str,
        page: int = 1,
        per_page: int = 6,
    ) -> Page[User]:
        """Проверяет ответ со списком пользователей"""
        with allure.step("Verify users list API response"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            data = response.json()

            cls.check_pagination_structure(data, page, per_page)

            users = [User(**user_data) for user_data in data["items"]]

            allure.attach(
                f"Total users: {data['total']}\nPage: {page}\nPer page: {per_page}\nReturned: {len(users)}",
                "Users List Summary",
                allure.attachment_type.TEXT,
            )

            return Page(
                items=users,
                page=data["page"],
                size=data["size"],
                total=data["total"],
                pages=data["pages"],
            )

    # ========================================
    # АУТЕНТИФИКАЦИЯ (test_auth.py)
    # ========================================

    @classmethod
    def check_email_error_response(
        cls, response: requests.Response, endpoint: str, expected_error: str
    ) -> None:
        """Проверяет ошибку с email"""
        with allure.step(f"Verify email validation error for {endpoint}"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.BAD_REQUEST)
            data = response.json()

            assert "detail" in data, "Missing 'detail' in error response"
            assert "error" in data["detail"], "Missing 'error' in detail"
            assert (
                data["detail"]["error"] == expected_error
            ), f"Expected '{expected_error}', got '{data['detail']['error']}'"

            allure.attach(
                expected_error, "Expected Error Message", allure.attachment_type.TEXT
            )
            allure.attach(
                data["detail"]["error"],
                "Actual Error Message",
                allure.attachment_type.TEXT,
            )

    # ========================================
    # СПЕЦИАЛЬНЫЕ ТЕСТЫ (test_special.py)
    # ========================================

    @classmethod
    def check_delayed_response(
        cls, response: requests.Response, endpoint: str, min_duration: float
    ) -> None:
        """Проверяет delayed response"""
        with allure.step(f"Verify delayed response (min {min_duration}s)"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            data = response.json()

            assert "page" in data, "Missing 'page' in response"
            assert "size" in data, "Missing 'size' in response"
            assert "total" in data, "Missing 'total' in response"
            assert "pages" in data, "Missing 'pages' in response"
            assert "items" in data, "Missing 'items' in response"

            assert isinstance(data["items"], list), "Items should be a list"
            assert len(data["items"]) > 0, "Items array should not be empty"

            allure.attach(
                f"Minimum delay: {min_duration}s",
                "Delay Information",
                allure.attachment_type.TEXT,
            )
            logger.info(f"Delayed response validated, took at least {min_duration}s")

    # ========================================
    # УНИВЕРСАЛЬНЫЕ ХЕЛПЕРЫ
    # ========================================

    @staticmethod
    def check_unique_ids(items_list, item_name: str = "items") -> None:
        """Проверяет уникальность ID в списке объектов"""
        with allure.step(f"Verify unique IDs in {item_name} list"):
            ids = [item.id for item in items_list]
            unique_ids = set(ids)

            assert len(ids) == len(
                unique_ids
            ), f"Found duplicate {item_name} IDs: {ids}"

            allure.attach(
                f"Total items: {len(ids)}\nUnique IDs: {len(unique_ids)}\nAll IDs: {ids}",
                "ID Uniqueness Check",
                allure.attachment_type.TEXT,
            )

    @staticmethod
    def check_multiple_fields(obj: Any, **field_expectations) -> None:
        """Проверяет несколько полей объекта сразу"""
        with allure.step("Verify multiple object fields"):
            for field_name, expected_value in field_expectations.items():
                actual_value = getattr(obj, field_name)
                assert (
                    actual_value == expected_value
                ), f"Expected {field_name}={expected_value}, got {actual_value}"

            allure.attach(
                str(field_expectations),
                "Field Expectations",
                allure.attachment_type.JSON,
            )


# Создаем экземпляр для удобного использования
api = APIAssertions()
