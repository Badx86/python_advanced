"""
Автотесты API с использованием Fluent паттерна:
- Fluent API клиент с автоматической валидацией схем
- Управление тестовыми данными с автоматической очисткой
- Интеграция с Allure для детальной отчетности
- Проверки бизнес-логики и целостности данных
"""

import allure
import pytest
import logging
import time
from tests.assertions import APIAssertions

logger = logging.getLogger(__name__)


@allure.feature("API Validation & Business Logic: User Management")
@pytest.mark.schema
class TestUserManagementWithSchemas:
    """Проверка управления пользователями через fluent API с валидацией схем"""

    @allure.title("User list with automatic validation")
    @pytest.mark.smoke
    def test_users_list_validated(self, api):
        """Проверка получения списка пользователей с автоматической валидацией схемы ответа"""
        response = api.users().list(page=1, size=6)
        APIAssertions.check_fluent_users_list(response)
        logger.info("Users list validated with fluent API")

    @allure.title("Full user lifecycle with validation")
    def test_user_full_lifecycle(self, api, user_data, test_data):
        """Проверка полного жизненного цикла пользователя: создание, чтение, обновление"""
        APIAssertions.check_fluent_user_lifecycle(api, user_data, test_data)
        logger.info("User lifecycle completed with fluent API")

    @allure.title("Non-existent user returns proper error")
    def test_user_not_found_validation(self, api):
        """Проверка корректного возврата ошибки 404 для несуществующего пользователя"""
        response = api.users().get_404(999999)
        APIAssertions.check_fluent_user_not_found(response)
        logger.info("404 error properly validated with fluent API")


@allure.feature("API Validation & Business Logic: Resource Management")
@pytest.mark.schema
class TestResourceManagementWithSchemas:
    """Проверка управления ресурсами через fluent API с валидацией схем"""

    @allure.title("Resource CRUD with schema validation")
    def test_resource_operations(self, api, resource_data, test_data):
        """Проверка CRUD операций с ресурсами и валидации схем ответов"""
        APIAssertions.check_fluent_resource_operations(api, resource_data, test_data)
        logger.info("Resource operations completed with fluent API")

    @allure.title("Resource list pagination validation")
    @pytest.mark.pagination
    def test_resources_pagination(self, api, pagination_params):
        """Проверка корректности пагинации списка ресурсов"""
        page, size = pagination_params["page"], pagination_params["size"]
        response = api.resources().list(page=page, size=size)
        APIAssertions.check_fluent_resource_pagination(response, page, size)
        logger.info(f"Resource pagination validated: page {page}, size {size}")


@allure.feature("Authentication & Security: User Authentication")
@pytest.mark.auth
class TestAuthenticationWithSchemas:
    """Проверка аутентификации пользователей через fluent API"""

    @allure.title("Successful user registration flow")
    def test_registration_flow(self, api, auth_data):
        """Проверка успешного процесса регистрации пользователя"""
        response = api.auth().register(auth_data["email"], auth_data["password"])
        APIAssertions.check_fluent_auth_registration(response)
        logger.info("Registration flow completed with fluent API")

    @allure.title("Successful user login flow")
    def test_login_flow(self, api, auth_data):
        """Проверка успешного процесса авторизации пользователя"""
        response = api.auth().login(auth_data["email"], auth_data["password"])
        APIAssertions.check_fluent_auth_login(response)
        logger.info("Login flow completed with fluent API")


@allure.feature("Service Monitoring")
@pytest.mark.smoke
class TestSystemHealthWithSchemas:
    """Проверка состояния системы и мониторинг сервиса"""

    @allure.title("Comprehensive system status check")
    def test_system_status_comprehensive(self, api):
        """Комплексная проверка статуса системы и всех компонентов"""
        response = api.system().status()
        APIAssertions.check_fluent_system_health(response)
        logger.info("System health check completed with fluent API")


@allure.feature("Response Time")
@pytest.mark.slow
class TestPerformanceWithSchemas:
    """Проверка производительности и времени отклика API"""

    @allure.title("Delayed response validation")
    @pytest.mark.parametrize("delay", [1, 2])
    def test_delayed_response_control(self, api, delay):
        """Проверка функциональности задержанного ответа API"""
        start_time = time.time()
        response = api.users().list(page=1, size=6, delay=delay)
        actual_duration = time.time() - start_time

        APIAssertions.check_fluent_delayed_response(response, delay, actual_duration)
        logger.info(f"Delayed response validated: {actual_duration:.2f}s")


@allure.feature("Business Rules")
@pytest.mark.crud
class TestBusinessRulesWithSchemas:
    """Проверка бизнес-правил и целостности данных"""

    @allure.title("Data consistency across multiple operations")
    def test_data_consistency_across_operations(self, api, test_data, fake):
        """Проверка консистентности данных при выполнении множественных операций"""
        APIAssertions.check_fluent_data_consistency(api, test_data, fake)
        logger.info("Data consistency validated with fluent API")

    @allure.title("Parallel operations safety")
    def test_parallel_operations_safety(self, api, test_data, resource_data):
        """Проверка безопасности параллельных операций и сохранения целостности данных"""
        APIAssertions.check_fluent_parallel_operations(api, test_data, resource_data)
        logger.info("Parallel operations safety validated with fluent API")
