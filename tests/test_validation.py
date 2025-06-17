import allure
import logging
from http import HTTPStatus
from tests.assertions import api

logger = logging.getLogger(__name__)


@allure.epic("Data Validation & Error Handling")
@allure.feature("Input Validation")
class TestValidation:
    """Тесты валидации данных и HTTP ошибок"""

    @allure.story("HTTP Method Validation")
    @allure.title("Method not allowed error")
    @allure.description(
        "Test unsupported HTTP methods should return 405 Method Not Allowed"
    )
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("api", "validation", "405", "http-methods")
    def test_method_not_allowed_405(self, api_client) -> None:
        """Тест неподдерживаемых HTTP методов - должен возвращать 405"""
        # POST на GET эндпоинт
        response = api_client.post("/api/users/1")
        api.log_and_check_status(
            response, "POST /api/users/1", HTTPStatus.METHOD_NOT_ALLOWED
        )
        logger.info("Method POST correctly rejected on GET endpoint with 405")

    @allure.story("Required Fields Validation")
    @allure.title("Create user without name field")
    @allure.description(
        "Test creating user without required 'name' field should return 422"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "validation", "422", "required-fields", "user")
    def test_create_user_missing_name_field(self, api_client) -> None:
        """Тест создания пользователя без обязательного поля 'name'"""
        user_data = {"job": "developer"}

        response = api_client.post("/api/users", json=user_data)
        api.log_and_check_status(
            response, "POST /api/users", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info("User creation correctly failed without 'name' field (422)")

    @allure.story("Required Fields Validation")
    @allure.title("Create user without job field")
    @allure.description(
        "Test creating user without required 'job' field should return 422"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "validation", "422", "required-fields", "user")
    def test_create_user_missing_job_field(self, api_client) -> None:
        """Тест создания пользователя без обязательного поля 'job'"""
        user_data = {"name": "testuser"}

        response = api_client.post("/api/users", json=user_data)
        api.log_and_check_status(
            response, "POST /api/users", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info("User creation correctly failed without 'job' field (422)")
