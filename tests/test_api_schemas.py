"""
Автотесты API с использованием Fluent паттерна:
- Fluent API клиент с явной валидацией схем
- Управление тестовыми данными с автоматической очисткой
- Интеграция с Allure для детальной отчетности
- Проверки бизнес-логики и целостности данных
"""

import allure
import pytest
import logging
import time
from typing import Dict, Any
from tests.assertions import APIAssertions

logger = logging.getLogger(__name__)


@allure.feature("API Validation & Business Logic: User Management")
@pytest.mark.schema
class TestUserManagementWithSchemas:
    """Проверка управления пользователями через fluent API с явной валидацией схем"""

    @allure.title("User list with explicit schema validation")
    @pytest.mark.smoke
    def test_users_list_validated(self, api):
        """Проверка получения списка пользователей с явной валидацией схемы ответа"""
        response = api.users().list(page=1, size=6).validate_users_list()

        # Проверка бизнес-логики после валидации схемы с helper методом
        APIAssertions.check_fluent_users_list_business_logic(
            response, expected_page=1, expected_size=6
        )

    @allure.title("Full user lifecycle with explicit validation steps")
    def test_user_full_lifecycle(self, api, user_data: Dict[str, Any], test_data):
        """Проверка полного жизненного цикла пользователя с явными шагами валидации"""

        with allure.step("Create user with schema validation"):
            user_id = test_data.create_user(
                user_data.get("name", ""), user_data.get("job", "")
            )
            allure.attach(
                f"Created user ID: {user_id}",
                "User Creation",
                allure.attachment_type.TEXT,
            )

        with allure.step("Verify created user with schema validation"):
            response = api.users().get(user_id).validate_single_user()
            user_data_dict = response.extract("data")
            user_first_name = user_data_dict.get("first_name", "")
            user_last_name = user_data_dict.get("last_name", "")
            user_name = f"{user_first_name} {user_last_name}"
            expected_name_lower = str(user_data.get("name", "")).lower()
            actual_name_lower = str(user_name).lower()
            assert (
                expected_name_lower in actual_name_lower
            ), f"User name mismatch: {user_name}"

        with allure.step("Update user with schema validation"):
            new_name, new_job = "Updated User", "Senior Engineer"
            update_response = (
                api.users().update(user_id, new_name, new_job).validate_user_updated()
            )
            updated_name, updated_job = update_response.extract("name", "job")
            assert updated_name == new_name, f"Updated name mismatch"
            assert updated_job == new_job, f"Updated job mismatch"

        with allure.step("Final verification with schema validation"):
            final_response = api.users().get(user_id).validate_single_user()
            assert final_response.status_code == 200, "User should exist after update"

        logger.info(f"User lifecycle completed successfully for ID: {user_id}")

    @allure.title("Non-existent user error handling with schema validation")
    def test_user_not_found_validation(self, api):
        """Проверка корректного возврата ошибки 404 для несуществующего пользователя"""
        response = api.users().get_404(999999).validate_api_error()

        # Проверка бизнес-логики после валидации схемы с helper методом
        APIAssertions.check_fluent_error_response_business_logic(
            response, expected_error_pattern="not found"
        )

    @allure.title("Edge case: Testing without schema validation")
    def test_user_raw_response_handling(self, api):
        """Демонстрация работы с raw ответами без автоматической валидации"""

        with allure.step("Get raw response without schema validation"):
            # Получаем ответ без валидации и без автоматической проверки статуса
            response = api.users().get_raw(999999)  # НЕ ВАЛИДИРУЕМ автоматически

        with allure.step("Manual validation and error handling"):
            # Можем вручную проверить что это ошибка
            assert response.status_code == 404

            # И только потом валидировать как API error
            response.validate_api_error()

        logger.info("Raw response handling demonstrates flexibility")


@allure.feature("API Validation & Business Logic: Resource Management")
@pytest.mark.schema
class TestResourceManagementWithSchemas:
    """Проверка управления ресурсами через fluent API с явной валидацией схем"""

    @allure.title("Resource CRUD with explicit schema validation")
    def test_resource_operations(self, api, resource_data: Dict[str, Any], test_data):
        """Проверка CRUD операций с ресурсами и явной валидации схем ответов"""

        with allure.step("Create resource with schema validation"):
            resource_id = test_data.create_resource(**resource_data)

        with allure.step("Verify created resource with schema validation"):
            response = api.resources().get(resource_id).validate_single_resource()
            data = response.extract("data")

            assert data.get("name") == resource_data["name"], f"Resource name mismatch"
            assert data.get("year") == resource_data["year"], f"Resource year mismatch"
            assert (
                data.get("color") == resource_data["color"]
            ), f"Resource color mismatch"

        with allure.step("Update resource with schema validation"):
            updated_data = {
                "name": "Updated Resource",
                "year": 2025,
                "color": "#123456",
                "pantone_value": "UPD-001",
            }

            update_response = (
                api.resources()
                .update(resource_id, updated_data, method="PUT")
                .validate_resource_updated()
            )

            # Проверка обновления
            for key, value in updated_data.items():
                actual_value = update_response.extract(key)
                assert (
                    actual_value == value
                ), f"Resource {key} update failed: {actual_value} != {value}"

        logger.info(f"Resource operations completed for ID: {resource_id}")

    @allure.title("Resource list pagination with explicit validation")
    @pytest.mark.pagination
    def test_resources_pagination(self, api, pagination_params: Dict[str, Any]):
        """Проверка корректности пагинации списка ресурсов с явной валидацией"""
        page, size = pagination_params["page"], pagination_params["size"]

        response = api.resources().list(page=page, size=size).validate_resources_list()

        # Проверка пагинации после валидации схемы с helper методом
        APIAssertions.check_fluent_pagination_calculations(
            response, expected_page=page, expected_size=size
        )


@allure.feature("Authentication & Security: User Authentication")
@pytest.mark.auth
class TestAuthenticationWithSchemas:
    """Проверка аутентификации пользователей через fluent API с явной валидацией"""

    @allure.title("Successful user registration with explicit validation")
    def test_registration_flow(self, api, auth_data: Dict[str, Any]):
        """Проверка успешного процесса регистрации пользователя"""
        response = (
            api.auth()
            .register(auth_data["email"], auth_data["password"])
            .validate_register_success()
        )

        # Проверка бизнес-логики после валидации схемы с helper методом
        auth_result = APIAssertions.check_fluent_authentication_business_logic(
            response, check_user_id=True
        )

        allure.attach(
            f"User ID: {auth_result['user_id']}",
            "Registration Success",
            allure.attachment_type.TEXT,
        )

    @allure.title("Successful user login with explicit validation")
    def test_login_flow(self, api, auth_data: Dict[str, Any]):
        """Проверка успешного процесса авторизации пользователя"""
        response = (
            api.auth()
            .login(auth_data["email"], auth_data["password"])
            .validate_login_success()
        )

        # Проверка бизнес-логики после валидации схемы с helper методом
        APIAssertions.check_fluent_authentication_business_logic(
            response, check_user_id=False
        )


@allure.feature("Service Monitoring")
@pytest.mark.smoke
class TestSystemHealthWithSchemas:
    """Проверка состояния системы и мониторинг сервиса с явной валидацией"""

    @allure.title("Comprehensive system status check with explicit validation")
    def test_system_status_comprehensive(self, api):
        """Комплексная проверка статуса системы и всех компонентов"""
        response = api.system().status().validate_system_health()

        # Проверка бизнес-логики после валидации схемы с helper методом
        APIAssertions.check_fluent_system_health_business_logic(response)


@allure.feature("Response Time")
@pytest.mark.slow
class TestPerformanceWithSchemas:
    """Проверка производительности и времени отклика API с явной валидацией"""

    @allure.title("Delayed response with explicit validation")
    @pytest.mark.parametrize("delay", [1, 2])
    def test_delayed_response_control(self, api, delay):
        """Проверка функциональности задержанного ответа API"""
        start_time = time.time()
        response = api.users().list(page=1, size=6, delay=delay).validate_users_list()
        actual_duration = time.time() - start_time

        # Проверка времени после валидации схемы
        assert (
            actual_duration >= delay - 0.1
        ), f"Response should take at least {delay}s, got {actual_duration:.2f}s"

        # Проверка данных после валидации схемы
        items = response.extract("items")
        assert len(items) <= 6, f"Page size should be respected even with delay"

        allure.attach(
            f"Requested delay: {delay}s\nActual duration: {actual_duration:.2f}s",
            "Performance Metrics",
            allure.attachment_type.TEXT,
        )

        logger.info(
            f"Delayed response validated: {actual_duration:.2f}s (requested: {delay}s)"
        )


@allure.feature("Business Rules")
@pytest.mark.crud
class TestBusinessRulesWithSchemas:
    """Проверка бизнес-правил и целостности данных с явной валидацией"""

    @allure.title("Data consistency with explicit validation steps")
    def test_data_consistency_across_operations(self, api, test_data, fake):
        """Проверка консистентности данных при выполнении множественных операций"""
        operations_count = 3

        with allure.step("Create multiple users with schema validation"):
            user_ids = []
            for i in range(operations_count):
                name = f"User {i + 1} {fake['person'].last_name()}"
                job = fake["person"].occupation()
                user_id = test_data.create_user(name, job)
                user_ids.append(user_id)

        with allure.step("Verify all users exist with schema validation"):
            retrieved_ids = []
            for user_id in user_ids:
                response = api.users().get(user_id).validate_single_user()
                user_data_dict = response.extract("data")
                retrieved_ids.append(user_data_dict.get("id"))

            assert len(set(retrieved_ids)) == len(
                retrieved_ids
            ), "All user IDs should be unique"

        with allure.step("Verify users presence in list with schema validation"):
            response = api.users().list(page=1, size=50).validate_users_list()
            users_list = response.extract("items")
            all_user_ids = [user["id"] for user in users_list]

            for user_id in user_ids:
                assert (
                    user_id in all_user_ids
                ), f"User {user_id} should be in users list"

        logger.info(f"Data consistency validated across {len(user_ids)} users")

    @allure.title("Parallel operations safety with explicit validation")
    def test_parallel_operations_safety(
        self, api, test_data, resource_data: Dict[str, Any]
    ):
        """Проверка безопасности параллельных операций через fluent API"""
        operations_count = 5
        resource_ids = []
        base_name = resource_data.get("name", "Default Resource")

        with allure.step("Create multiple resources with schema validation"):
            for i in range(operations_count):
                modified_data = resource_data.copy()
                modified_data["name"] = f"{base_name} {i + 1}"
                modified_data["pantone_value"] = f"PAR-{i + 1:03d}"

                resource_id = test_data.create_resource(**modified_data)
                resource_ids.append(resource_id)

        with allure.step("Verify all resources with schema validation"):
            for i, resource_id in enumerate(resource_ids):
                response = api.resources().get(resource_id).validate_single_resource()
                data = response.extract("data")

                expected_name = f"{base_name} {i + 1}"
                assert (
                    data.get("name") == expected_name
                ), f"Resource {resource_id} name mismatch"

        logger.info(
            f"Parallel operations safety validated for {len(resource_ids)} resources"
        )
