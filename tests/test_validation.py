import allure
import logging
from http import HTTPStatus
from tests.assertions import api

logger = logging.getLogger(__name__)


@allure.feature("Input Validation")
class TestValidation:
    """Тесты валидации данных и HTTP ошибок"""

    @allure.title("Method not allowed error")
    def test_method_not_allowed_405(self, api_client) -> None:
        """Тест неподдерживаемых HTTP методов - должен возвращать 405"""
        # POST на GET эндпоинт
        response = api_client.post("/api/users/1")
        api.log_and_check_status(
            response, "POST /api/users/1", HTTPStatus.METHOD_NOT_ALLOWED
        )
        logger.info("Method POST correctly rejected on GET endpoint with 405")

    @allure.title("Create user without name field")
    def test_create_user_missing_name_field(self, api_client) -> None:
        """Тест создания пользователя без обязательного поля 'name'"""
        user_data = {"job": "developer"}

        response = api_client.post("/api/users", json=user_data)
        api.log_and_check_status(
            response, "POST /api/users", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info("User creation correctly failed without 'name' field (422)")

    @allure.title("Create user without job field")
    def test_create_user_missing_job_field(self, api_client) -> None:
        """Тест создания пользователя без обязательного поля 'job'"""
        user_data = {"name": "testuser"}

        response = api_client.post("/api/users", json=user_data)
        api.log_and_check_status(
            response, "POST /api/users", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info("User creation correctly failed without 'job' field (422)")
