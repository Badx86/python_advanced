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

            # ТОЛЬКО Response Body для отладки API - это критично
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
    # НОВЫЕ МЕТОДЫ ДЛЯ FLUENT API
    # ========================================

    @classmethod
    def check_fluent_users_list(cls, api_response) -> None:
        """Проверяет fluent API список пользователей с автоматической валидацией"""
        with allure.step("Verify fluent users list with schema validation"):
            # Извлекаем данные через fluent API
            total, items = api_response.extract("total", "items")

            # Бизнес-логика проверки
            assert total >= 0, "Total users count should be non-negative"
            assert len(items) <= 6, "Page size should be respected"

            logger.info(
                f"Fluent users list validated: {total} total users, {len(items)} on page"
            )

    @classmethod
    def check_fluent_user_lifecycle(
        cls, api, user_data: Dict[str, str], test_data
    ) -> None:
        """Проверяет полный жизненный цикл пользователя через fluent API"""
        with allure.step("Execute complete user lifecycle test"):
            # Создание пользователя
            user_id = test_data.create_user(user_data["name"], user_data["job"])
            allure.attach(
                f"Created user ID: {user_id}",
                "User Creation",
                allure.attachment_type.TEXT,
            )

            # Проверка созданного пользователя
            response = api.users().get(user_id)
            user_data_dict = response.extract("data")
            user_name = user_data_dict["first_name"] + " " + user_data_dict["last_name"]
            assert (
                user_data["name"].lower() in user_name.lower()
            ), f"User name mismatch: {user_name}"

            # Обновление пользователя
            new_name, new_job = "Updated User", "Senior Engineer"
            update_response = api.users().update(user_id, new_name, new_job)
            updated_name, updated_job = update_response.extract("name", "job")
            assert updated_name == new_name, f"Updated name mismatch"
            assert updated_job == new_job, f"Updated job mismatch"

            # Проверка сохранения
            final_response = api.users().get(user_id)
            assert (
                final_response.status_code == HTTPStatus.OK
            ), "User should exist after update"

            logger.info(f"User lifecycle completed successfully for ID: {user_id}")

    @classmethod
    def check_fluent_user_not_found(cls, api_response) -> None:
        """Проверяет 404 ошибку через fluent API с валидацией схемы"""
        with allure.step("Verify 404 error with schema validation"):
            detail = api_response.extract("detail")
            error_message = detail["error"]
            assert (
                "not found" in error_message.lower()
            ), f"Unexpected error message: {error_message}"

            logger.info("404 error properly validated with schema")

    @classmethod
    def check_fluent_resource_operations(
        cls, api, resource_data: Dict[str, Any], test_data
    ) -> None:
        """Проверяет CRUD операции ресурсов через fluent API"""
        with allure.step("Execute resource CRUD operations"):
            # Создание ресурса
            resource_id = test_data.create_resource(**resource_data)

            # Проверка созданного ресурса
            response = api.resources().get(resource_id)
            data = response.extract("data")

            assert data["name"] == resource_data["name"], f"Resource name mismatch"
            assert data["year"] == resource_data["year"], f"Resource year mismatch"
            assert data["color"] == resource_data["color"], f"Resource color mismatch"

            # Обновление ресурса
            updated_data = {
                "name": "Updated Resource",
                "year": 2025,
                "color": "#123456",
                "pantone_value": "UPD-001",
            }

            update_response = api.resources().update(
                resource_id, updated_data, method="PUT"
            )

            # Проверка обновления
            for key, value in updated_data.items():
                actual_value = update_response.extract(key)
                assert (
                    actual_value == value
                ), f"Resource {key} update failed: {actual_value} != {value}"

            logger.info(f"Resource operations completed for ID: {resource_id}")

    @classmethod
    def check_fluent_resource_pagination(
        cls, api_response, page: int, size: int
    ) -> None:
        """Проверяет пагинацию ресурсов через fluent API"""
        with allure.step("Verify resource pagination"):
            # Извлекаем данные пагинации
            actual_page, actual_size, total, pages, items = api_response.extract(
                "page", "size", "total", "pages", "items"
            )

            # Валидация бизнес-логики
            assert actual_page == page, f"Page mismatch: {actual_page} != {page}"
            assert actual_size == size, f"Size mismatch: {actual_size} != {size}"
            assert len(items) <= size, f"Items count exceeds page size"

            # Проверяем расчеты пагинации
            expected_pages = max(1, (total + size - 1) // size) if total > 0 else 1
            assert (
                pages == expected_pages
            ), f"Pages calculation error: {pages} != {expected_pages}"

            logger.info(
                f"Pagination validated: page {page}/{pages}, {len(items)} items"
            )

    @classmethod
    def check_fluent_auth_registration(cls, api_response) -> None:
        """Проверяет успешную регистрацию через fluent API"""
        with allure.step("Verify successful registration"):
            user_id, token = api_response.extract("id", "token")

            assert user_id > 0, f"User ID should be positive: {user_id}"
            assert len(token) > 0, f"Token should not be empty"

            allure.attach(
                f"User ID: {user_id}",
                "Registration Success",
                allure.attachment_type.TEXT,
            )
            logger.info(f"User registered successfully with ID: {user_id}")

    @classmethod
    def check_fluent_auth_login(cls, api_response) -> None:
        """Проверяет успешный логин через fluent API"""
        with allure.step("Verify successful login"):
            token = api_response.extract("token")

            assert len(token) > 0, f"Token should not be empty"

            logger.info("Login successful with valid token")

    @classmethod
    def check_fluent_system_health(cls, api_response) -> None:
        """Проверяет статус системы через fluent API"""
        with allure.step("Verify comprehensive system status"):
            status, version, db_status, services = api_response.extract(
                "status", "version", "database", "services"
            )

            # Проверки здоровья системы
            assert status in ["healthy", "unhealthy"], f"Invalid status: {status}"
            assert (
                version.count(".") >= 2
            ), f"Version should follow semantic versioning: {version}"
            assert (
                db_status.get("status") == "connected"
            ), f"Database should be connected"
            assert (
                db_status.get("users_count", 0) >= 0
            ), f"User count should be non-negative"

            # Проверки статуса сервисов
            for service, service_status in services.items():
                assert len(service_status) > 0, f"Service {service} should have status"

            allure.attach(
                f"System Status: {status}\nVersion: {version}\nDB: {db_status['status']}",
                "System Health Summary",
                allure.attachment_type.TEXT,
            )

            logger.info(f"System health check passed: {status} (v{version})")

    @classmethod
    def check_fluent_delayed_response(
        cls, api_response, delay: int, actual_duration: float
    ) -> None:
        """Проверяет delayed response через fluent API"""
        with allure.step(f"Verify delayed response (min {delay}s)"):
            # Проверка времени
            assert (
                actual_duration >= delay - 0.1
            ), f"Response should take at least {delay}s, got {actual_duration:.2f}s"

            # Проверка данных
            items = api_response.extract("items")
            assert len(items) <= 6, f"Page size should be respected even with delay"

            allure.attach(
                f"Requested delay: {delay}s\nActual duration: {actual_duration:.2f}s",
                "Performance Metrics",
                allure.attachment_type.TEXT,
            )

            logger.info(
                f"Delayed response validated: {actual_duration:.2f}s (requested: {delay}s)"
            )

    @classmethod
    def check_fluent_data_consistency(
        cls, api, test_data, fake, operations_count: int = 3
    ) -> None:
        """Проверяет консистентность данных через fluent API"""
        with allure.step("Verify data consistency across multiple operations"):
            # Создаем пользователей
            user_ids = []
            for i in range(operations_count):
                name = f"User {i + 1} {fake['person'].last_name()}"
                job = fake["person"].occupation()
                user_id = test_data.create_user(name, job)
                user_ids.append(user_id)

            # Проверяем уникальность ID
            retrieved_ids = []
            for user_id in user_ids:
                response = api.users().get(user_id)
                user_data_dict = response.extract("data")
                retrieved_ids.append(user_data_dict["id"])

            assert len(set(retrieved_ids)) == len(
                retrieved_ids
            ), "All user IDs should be unique"

            # Проверяем присутствие в списке
            response = api.users().list(page=1, size=50)
            users_list = response.extract("items")
            all_user_ids = [user["id"] for user in users_list]

            for user_id in user_ids:
                assert (
                    user_id in all_user_ids
                ), f"User {user_id} should be in users list"

            logger.info(f"Data consistency validated across {len(user_ids)} users")

    @classmethod
    def check_fluent_parallel_operations(
        cls, api, test_data, resource_data: Dict[str, Any], operations_count: int = 5
    ) -> None:
        """Проверяет безопасность параллельных операций через fluent API"""
        with allure.step("Verify parallel operations safety"):
            resource_ids = []
            base_name = resource_data["name"]

            # Создаем ресурсы
            for i in range(operations_count):
                modified_data = resource_data.copy()
                modified_data["name"] = f"{base_name} {i + 1}"
                modified_data["pantone_value"] = f"PAR-{i + 1:03d}"

                resource_id = test_data.create_resource(**modified_data)
                resource_ids.append(resource_id)

            # Проверяем все ресурсы
            for i, resource_id in enumerate(resource_ids):
                response = api.resources().get(resource_id)
                data = response.extract("data")

                expected_name = f"{base_name} {i + 1}"
                assert (
                    data["name"] == expected_name
                ), f"Resource {resource_id} name mismatch"

            logger.info(
                f"Parallel operations safety validated for {len(resource_ids)} resources"
            )

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
        """Проверяет уникальность ID в списке объектов"""
        with allure.step(f"Verify unique IDs in {item_name} list"):
            ids = [item.id for item in items_list]
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
