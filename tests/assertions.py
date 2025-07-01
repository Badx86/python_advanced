import allure
import logging
from typing import Dict, Any, Sequence
from http import HTTPStatus
import requests
from fastapi_pagination import Page
from sqlmodel import Session
from app.models import (
    SingleUserResponse,
    SingleResourceResponse,
    UserResponse,
    User,
    Resource,
)

# Curlify для генерации curl команд
try:
    import curlify
except ImportError:
    curlify = None

logger = logging.getLogger(__name__)


# ========================================
# ХЕЛПЕРЫ ДЛЯ РАБОТЫ С БД (вместо database layer)
# ========================================


def get_user_from_db(user_id: int) -> User | None:
    """Получить пользователя из БД"""
    try:
        from app.database.engine import engine

        with Session(engine) as session:
            return session.get(User, user_id)
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None


def get_resource_from_db(resource_id: int) -> Resource | None:
    """Получить ресурс из БД"""
    try:
        from app.database.engine import engine

        with Session(engine) as session:
            return session.get(Resource, resource_id)
    except Exception as e:
        logger.error(f"Error getting resource {resource_id}: {e}")
        return None


class APIAssertions:
    """Класс для всех проверок API ответов + БД с Allure отчетностью"""

    # ========================================
    # БАЗОВЫЕ ПРОВЕРКИ
    # ========================================

    @staticmethod
    def log_curl_command(
        response: requests.Response, title: str = "cURL Command"
    ) -> None:
        """Логирует cURL команду в Allure отчет"""
        if curlify:
            try:
                curl_cmd = curlify.to_curl(response.request)
                allure.attach(curl_cmd, title, allure.attachment_type.TEXT)
                logger.debug(f"cURL: {curl_cmd}")
            except Exception as e:
                logger.warning(f"Failed to generate cURL: {e}")

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

            # Логируем cURL при ошибках
            if response.status_code >= 400:
                APIAssertions.log_curl_command(
                    response, f"🐛 Debug {response.status_code} Error"
                )

            # ТОЛЬКО Response Body для отладки API
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

            # Только Error Message
            allure.attach(
                data["detail"]["error"], "Error Message", allure.attachment_type.TEXT
            )

    # ========================================
    # ХЕЛПЕРЫ ДЛЯ FLUENT API
    # ========================================

    @classmethod
    def check_fluent_users_list_business_logic(
        cls, api_response, expected_page: int, expected_size: int
    ) -> None:
        """Проверяет бизнес-логику списка пользователей (после валидации схемы)"""
        with allure.step("Verify users list business logic"):
            # Предполагается что схема уже валидирована, проверяем только бизнес-логику
            total, items, page, size = api_response.extract(
                "total", "items", "page", "size"
            )

            # Проверки пагинации
            assert page == expected_page, f"Page mismatch: {page} != {expected_page}"
            assert size == expected_size, f"Size mismatch: {size} != {expected_size}"
            assert (
                len(items) <= expected_size
            ), f"Items count {len(items)} exceeds page size {expected_size}"
            assert total >= 0, "Total users count should be non-negative"

            # Проверки уникальности ID
            cls.check_unique_ids(items, "user")

            logger.info(
                f"Users list business logic validated: {total} total, {len(items)} on page {page}"
            )

    @classmethod
    def check_fluent_resource_business_logic(
        cls, api_response, expected_resource_data: Dict[str, Any]
    ) -> None:
        """Проверяет бизнес-логику ресурса"""
        with allure.step("Verify resource business logic"):
            # Предполагается что схема уже валидирована, проверяем только бизнес-логику
            data = api_response.extract("data")

            assert (
                data["name"] == expected_resource_data["name"]
            ), f"Resource name mismatch"
            assert (
                data["year"] == expected_resource_data["year"]
            ), f"Resource year mismatch"
            assert (
                data["color"] == expected_resource_data["color"]
            ), f"Resource color mismatch"
            assert (
                data["pantone_value"] == expected_resource_data["pantone_value"]
            ), f"Resource pantone mismatch"

            logger.info(
                f"Resource business logic validated: {data['name']} ({data['year']})"
            )

    @classmethod
    def check_fluent_user_creation_business_logic(
        cls, api_response, expected_name: str, expected_job: str
    ) -> int:
        """Проверяет бизнес-логику создания пользователя"""
        with allure.step("Verify user creation business logic"):
            # Предполагается что схема уже валидирована, проверяем только бизнес-логику
            name, job, user_id, created_at = api_response.extract(
                "name", "job", "id", "createdAt"
            )

            assert (
                name == expected_name
            ), f"Created user name mismatch: {name} != {expected_name}"
            assert (
                job == expected_job
            ), f"Created user job mismatch: {job} != {expected_job}"
            assert user_id is not None, "User ID should not be None"
            assert created_at is not None, "CreatedAt should not be None"

            user_id_int = int(user_id)
            assert user_id_int > 0, f"User ID should be positive: {user_id_int}"

            logger.info(
                f"User creation business logic validated: {name} ({job}) with ID {user_id_int}"
            )
            return user_id_int

    @classmethod
    def check_fluent_pagination_calculations(
        cls, api_response, expected_page: int, expected_size: int
    ) -> None:
        """Проверяет математику пагинации"""
        with allure.step("Verify pagination calculations"):
            # Предполагается что схема уже валидирована, проверяем только расчеты
            page, size, total, pages, items = api_response.extract(
                "page", "size", "total", "pages", "items"
            )

            # Проверяем что параметры соответствуют запрошенным
            assert page == expected_page, f"Page mismatch: {page} != {expected_page}"
            assert size == expected_size, f"Size mismatch: {size} != {expected_size}"

            # Проверяем математику пагинации
            expected_pages = max(1, (total + size - 1) // size) if total > 0 else 1
            assert (
                pages == expected_pages
            ), f"Pages calculation error: {pages} != {expected_pages}"

            # Проверяем количество элементов на странице
            if page <= pages and total > 0:
                max_items_on_page = min(size, total - (page - 1) * size)
                assert (
                    len(items) <= max_items_on_page
                ), f"Too many items on page: {len(items)} > {max_items_on_page}"

            logger.info(
                f"Pagination calculations verified: page {page}/{pages}, {len(items)} items"
            )

    @classmethod
    def check_fluent_authentication_business_logic(
        cls, api_response, check_user_id: bool = True
    ) -> Dict[str, Any]:
        """Проверяет бизнес-логику аутентификации"""
        with allure.step("Verify authentication business logic"):
            # Предполагается что схема уже валидирована, проверяем только бизнес-логику
            token = api_response.extract("token")

            assert token is not None, "Token should not be None"
            assert len(token) > 0, "Token should not be empty"
            assert len(token) >= 10, f"Token seems too short: {len(token)} chars"

            result = {"token": token}

            if check_user_id:
                user_id = api_response.extract("id")
                assert (
                    user_id is not None
                ), "User ID should not be None for registration"
                assert isinstance(
                    user_id, int
                ), f"User ID should be int, got {type(user_id)}"
                assert user_id > 0, f"User ID should be positive: {user_id}"
                result["user_id"] = user_id
                logger.info(
                    f"Authentication business logic validated: token length {len(token)}, user ID {user_id}"
                )
            else:
                logger.info(
                    f"Authentication business logic validated: token length {len(token)}"
                )

            return result

    @classmethod
    def check_fluent_system_health_business_logic(cls, api_response) -> None:
        """Проверяет бизнес-логику статуса системы"""
        with allure.step("Verify system health business logic"):
            # Предполагается что схема уже валидирована, проверяем только бизнес-логику
            status, version, database, data, services = api_response.extract(
                "status", "version", "database", "data", "services"
            )

            # Проверки общего статуса
            assert status in ["healthy", "unhealthy"], f"Invalid status: {status}"

            # Проверки версии
            version_parts = version.split(".")
            assert (
                len(version_parts) >= 3
            ), f"Version should follow semantic versioning: {version}"
            assert all(
                part.isdigit() for part in version_parts
            ), f"Version parts should be numeric: {version}"

            # Проверки базы данных
            db_status = database.get("status")
            assert (
                db_status == "connected"
            ), f"Database should be connected, got: {db_status}"

            users_count = database.get("users_count", 0)
            assert isinstance(
                users_count, int
            ), f"Users count should be int, got: {type(users_count)}"
            assert (
                users_count >= 0
            ), f"Users count should be non-negative: {users_count}"

            # Проверки данных
            users_data = data.get("users", {})
            resources_data = data.get("resources", {})

            assert users_data.get("loaded") is True, "Users data should be loaded"
            assert (
                resources_data.get("loaded") is True
            ), "Resources data should be loaded"

            # Проверки сервисов
            assert len(services) > 0, "Services dict should not be empty"
            for service_name, service_status in services.items():
                assert isinstance(
                    service_status, str
                ), f"Service {service_name} status should be string"
                assert (
                    len(service_status) > 0
                ), f"Service {service_name} status should not be empty"

            allure.attach(
                f"System Status: {status}\nVersion: {version}\nDB: {db_status}",
                "System Health Summary",
                allure.attachment_type.TEXT,
            )

            logger.info(
                f"System health business logic validated: {status} (v{version})"
            )

    @classmethod
    def check_fluent_error_response_business_logic(
        cls, api_response, expected_error_pattern: str = None
    ) -> None:
        """Проверяет бизнес-логику ошибок API"""
        with allure.step("Verify API error business logic"):
            # Предполагается что схема уже валидирована, проверяем только бизнес-логику
            detail = api_response.extract("detail")
            error_message = detail["error"]

            assert isinstance(
                error_message, str
            ), f"Error message should be string, got: {type(error_message)}"
            assert len(error_message) > 0, "Error message should not be empty"

            if expected_error_pattern:
                assert (
                    expected_error_pattern.lower() in error_message.lower()
                ), f"Expected error pattern '{expected_error_pattern}' not found in '{error_message}'"

            logger.info(f"API error business logic validated: {error_message}")

    # ========================================
    # ПРОВЕРКИ БД ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
    # ========================================

    @staticmethod
    def check_user_in_database(user_id: int, expected_name: str = None) -> User:
        """Проверяет что пользователь существует в БД"""
        with allure.step(f"Query database for user {user_id}"):
            db_user = get_user_from_db(user_id)
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

            logger.info(
                f"User {user_id} verified in database: {db_user.first_name} {db_user.last_name}"
            )
            return db_user

    @staticmethod
    def check_user_not_in_database(user_id: int) -> None:
        """Проверяет что пользователь НЕ существует в БД"""
        with allure.step(f"Verify user {user_id} is deleted from database"):
            db_user = get_user_from_db(user_id)
            assert (
                db_user is None
            ), f"User {user_id} should be deleted but still exists in database"

            logger.info(f"User {user_id} confirmed deleted from database")

    @staticmethod
    def check_user_updated_in_database(
        user_id: int, expected_name: str, original_user: User
    ) -> User:
        """Проверяет что пользователь обновился в БД"""
        with allure.step(f"Verify user {user_id} is updated in database"):
            updated_user = get_user_from_db(user_id)
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
            db_resource = get_resource_from_db(resource_id)
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

            logger.info(
                f"Resource {resource_id} verified in database: {db_resource.name} ({db_resource.year})"
            )
            return db_resource

    @staticmethod
    def check_resource_not_in_database(resource_id: int) -> None:
        """Проверяет что ресурс НЕ существует в БД"""
        with allure.step(f"Verify resource {resource_id} is deleted from database"):
            db_resource = get_resource_from_db(resource_id)
            assert (
                db_resource is None
            ), f"Resource {resource_id} should be deleted but still exists in database"

            logger.info(f"Resource {resource_id} confirmed deleted from database")

    @staticmethod
    def check_resource_updated_in_database(
        resource_id: int, expected_data: dict
    ) -> Resource:
        """Проверяет что ресурс обновился в БД"""
        with allure.step(f"Verify resource {resource_id} is updated in database"):
            updated_resource = get_resource_from_db(resource_id)
            assert (
                updated_resource is not None
            ), f"Resource {resource_id} not found after update"

            assert (
                updated_resource.name == expected_data["name"]
            ), f"DB name not updated: '{updated_resource.name}' != '{expected_data['name']}'"
            assert (
                updated_resource.year == expected_data["year"]
            ), f"DB year not updated: {updated_resource.year} != {expected_data['year']}"
            assert (
                updated_resource.color == expected_data["color"]
            ), f"DB color not updated: '{updated_resource.color}' != '{expected_data['color']}'"
            assert (
                updated_resource.pantone_value == expected_data["pantone_value"]
            ), f"DB pantone_value not updated: '{updated_resource.pantone_value}' != '{expected_data['pantone_value']}'"

            logger.info(
                f"Resource {resource_id} updated in database: {updated_resource.name} ({updated_resource.year})"
            )
            return updated_resource

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
    ) -> UserResponse:
        """Проверяет ответ создания пользователя (API + БД)"""
        with allure.step(f"Send POST request to create user: {expected_name}"):
            pass

        with allure.step("Verify user creation API response"):
            # 1. API проверка
            cls.log_and_check_status(response, endpoint, HTTPStatus.CREATED)
            create_response = UserResponse(**response.json())

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
    ) -> UserResponse:
        """Проверяет ответ обновления пользователя (API + БД)"""
        with allure.step(f"Send PUT/PATCH request to update user {user_id}"):
            pass

        with allure.step("Verify user update API response"):
            # 1. API проверка
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            update_response = UserResponse(**response.json())

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
            pass

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
        with allure.step(
            f"Send POST request to create resource: {expected_resource['name']}"
        ):
            pass

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

    @classmethod
    def check_update_resource_response(
        cls,
        response: requests.Response,
        endpoint: str,
        expected_resource: dict,
        resource_id: int,
    ) -> dict:
        """Проверяет ответ обновления ресурса (API + БД)"""
        with allure.step(f"Send PUT/PATCH request to update resource {resource_id}"):
            pass

        with allure.step("Verify resource update API response"):
            # 1. API проверка
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            data = response.json()

            assert data["name"] == expected_resource["name"]
            assert data["year"] == expected_resource["year"]
            assert data["color"] == expected_resource["color"]
            assert data["pantone_value"] == expected_resource["pantone_value"]
            assert "updatedAt" in data and data["updatedAt"] is not None

        with allure.step("Verify resource changes in database"):
            # 2. БД проверка
            cls.check_resource_updated_in_database(resource_id, expected_resource)

        return data

    @classmethod
    def check_delete_resource_response(
        cls, response: requests.Response, endpoint: str, resource_id: int
    ) -> None:
        """Проверяет ответ удаления ресурса (API + БД)"""
        with allure.step(f"Send DELETE request for resource {resource_id}"):
            pass

        with allure.step("Verify resource deletion API response"):
            # 1. API проверка
            cls.log_and_check_status(response, endpoint, HTTPStatus.NO_CONTENT)

        with allure.step("Verify resource removed from database"):
            # 2. БД проверка
            cls.check_resource_not_in_database(resource_id)

    # ========================================
    # ТЕСТЫ ПОЛЬЗОВАТЕЛЕЙ И РЕСУРСОВ (test_users.py, test_resources.py)
    # ========================================

    @classmethod
    def check_user_response(
        cls, response: requests.Response, endpoint: str
    ) -> SingleUserResponse:
        """Проверяет ответ с одним пользователем"""
        with allure.step("Verify single user API response"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            user_response = SingleUserResponse(**response.json())

            return user_response

    @classmethod
    def check_resource_response(
        cls, response: requests.Response, endpoint: str
    ) -> SingleResourceResponse:
        """Проверяет ответ с одним ресурсом"""
        with allure.step("Verify single resource API response"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            resource_response = SingleResourceResponse(**response.json())

            return resource_response

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

            return Page(
                items=users,
                page=data["page"],
                size=data["size"],
                total=data["total"],
                pages=data["pages"],
            )

    @classmethod
    def check_resources_list_response(
        cls,
        response: requests.Response,
        endpoint: str,
        page: int = 1,
        per_page: int = 6,
    ) -> Page[Resource]:
        """Проверяет ответ со списком ресурсов"""
        with allure.step("Verify resources list API response"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            data = response.json()

            cls.check_pagination_structure(data, page, per_page)

            resources = [Resource(**resource_data) for resource_data in data["items"]]

            return Page(
                items=resources,
                page=data["page"],
                size=data["size"],
                total=data["total"],
                pages=data["pages"],
            )

    # ========================================
    # АУТЕНТИФИКАЦИЯ (test_auth.py)
    # ========================================

    @classmethod
    def check_register_success_response(
        cls, response: requests.Response, endpoint: str
    ) -> dict:
        """Проверяет успешный ответ регистрации"""
        with allure.step("Verify successful registration API response"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.CREATED)
            data = response.json()

            assert "id" in data, "Missing 'id' in registration response"
            assert "token" in data, "Missing 'token' in registration response"

            assert isinstance(
                data["id"], int
            ), f"ID should be integer, got {type(data['id'])}"
            assert isinstance(
                data["token"], str
            ), f"Token should be string, got {type(data['token'])}"
            assert data["id"] > 0, f"ID should be positive, got {data['id']}"
            assert len(data["token"]) > 0, "Token should not be empty"

            logger.info(f"Registration successful: ID={data['id']}")
            return data

    @classmethod
    def check_login_success_response(
        cls, response: requests.Response, endpoint: str
    ) -> dict:
        """Проверяет успешный ответ логина"""
        with allure.step("Verify successful login API response"):
            cls.log_and_check_status(response, endpoint, HTTPStatus.OK)
            data = response.json()

            assert "token" in data, "Missing 'token' in login response"
            assert isinstance(
                data["token"], str
            ), f"Token should be string, got {type(data['token'])}"
            assert len(data["token"]) > 0, "Token should not be empty"

            logger.info("Login successful")
            return data

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

            logger.info(f"Delayed response validated, took at least {min_duration}s")

    # ========================================
    # УНИВЕРСАЛЬНЫЕ ХЕЛПЕРЫ
    # ========================================

    @staticmethod
    def check_unique_ids(items_list, item_name: str = "items") -> None:
        """Проверяет уникальность ID в списке объектов или словарей"""
        with allure.step(f"Verify unique IDs in {item_name} list"):
            # Поддержка как объектов с атрибутами, так и словарей
            if items_list and hasattr(items_list[0], "id"):
                ids = [item.id for item in items_list]
            else:
                ids = [item["id"] for item in items_list]

            unique_ids = set(ids)

            assert len(ids) == len(
                unique_ids
            ), f"Found duplicate {item_name} IDs: {ids}"

    @staticmethod
    def check_multiple_fields(obj: Any, **field_expectations) -> None:
        """Проверяет несколько полей объекта сразу"""
        with allure.step("Verify multiple object fields"):
            for field_name, expected_value in field_expectations.items():
                actual_value = getattr(obj, field_name)
                assert (
                    actual_value == expected_value
                ), f"Expected {field_name}={expected_value}, got {actual_value}"

    # ========================================
    # ПРОВЕРКИ ПАГИНАЦИИ
    # ========================================

    @staticmethod
    def check_pagination_pages_calculation(page_obj: Any, size: int) -> None:
        """Проверяет правильность расчета количества страниц"""
        with allure.step(f"Verify pages calculation for size={size}"):
            import math

            expected_pages = (
                math.ceil(page_obj.total / size) if page_obj.total > 0 else 1
            )

            assert page_obj.pages == expected_pages, (
                f"Pages calculation wrong: expected {expected_pages}, got {page_obj.pages} "
                f"(total={page_obj.total}, size={size})"
            )

            logger.info(
                f"Pages calculation correct: {page_obj.total} total / {size} size = {page_obj.pages} pages"
            )

    @staticmethod
    def check_pagination_items_count(page_obj: Any, page: int, size: int) -> None:
        """Проверяет правильность количества элементов на странице"""
        with allure.step(f"Verify items count for page={page}, size={size}"):
            if page <= page_obj.pages:
                expected_items = min(size, page_obj.total - (page - 1) * size)
                actual_items = len(page_obj.items)

                assert (
                    actual_items == expected_items
                ), f"Items count wrong: expected {expected_items}, got {actual_items} (page={page}, size={size})"

                logger.info(
                    f"Items count correct: page {page} has {actual_items} items (expected {expected_items})"
                )

    @staticmethod
    def check_pagination_different_data(
        first_page_items: Sequence[Any],
        second_page_items: Sequence[Any],
        entity_type: str,
    ) -> None:
        """Проверяет что данные на разных страницах действительно разные"""
        with allure.step(
            f"Verify different pages contain different {entity_type} data"
        ):
            # Извлекаем ключевые поля для сравнения
            if entity_type == "user":
                first_page_data = [
                    (item.id, item.email, item.first_name) for item in first_page_items
                ]
                second_page_data = [
                    (item.id, item.email, item.first_name) for item in second_page_items
                ]
            elif entity_type == "resource":
                first_page_data = [
                    (item.id, item.name, item.year) for item in first_page_items
                ]
                second_page_data = [
                    (item.id, item.name, item.year) for item in second_page_items
                ]
            else:
                raise ValueError(f"Unknown entity_type: {entity_type}")

            assert (
                first_page_data != second_page_data
            ), f"Different pages should return different {entity_type} data"

            # Проверяем уникальность ID между страницами
            # собираем все элементы в один список через unpacking
            combined_items: list[Any] = [*first_page_items, *second_page_items]
            APIAssertions.check_unique_ids(
                combined_items, f"{entity_type} across pages"
            )

            logger.info(f"Different pages contain unique {entity_type} data")

    @staticmethod
    def check_pagination_empty_page(page_obj: Any) -> None:
        """Проверяет что страница за пределами доступных возвращает пустой результат"""
        with allure.step("Verify page beyond available returns empty items"):
            actual_items_count = len(page_obj.items)

            assert (
                actual_items_count == 0
            ), f"Page beyond available should return empty items, got {actual_items_count}"

            logger.info("Page beyond available correctly returns empty results")


# Создаем экземпляр для удобного использования
api = APIAssertions()
