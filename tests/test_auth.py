import allure
import logging
import pytest
from http import HTTPStatus
from tests.assertions import api

logger = logging.getLogger(__name__)


@allure.feature("User Authentication")
@pytest.mark.auth
class TestAuth:
    """Тесты для аутентификации"""

    @allure.title("Successful registration")
    def test_register_successful(self, api_client) -> None:
        """Тест успешной регистрации"""
        register_data = {
            "email": "user@gmail.com",
            "password": "securepass123",
        }  # ← ИЗМЕНИТЬ ЭТО

        response = api_client.post("/api/register", json=register_data)
        api.check_register_success_response(response, "/api/register")
        logger.info("Registration successful with valid credentials")

    @allure.title("Successful login")
    def test_login_successful(self, api_client) -> None:
        """Тест успешного логина"""
        login_data = {"email": "user@gmail.com", "password": "securepass123"}  # ← И ЭТО

        response = api_client.post("/api/login", json=login_data)
        api.check_login_success_response(response, "/api/login")
        logger.info("Login successful with valid credentials")

    @allure.title("Register with invalid email formats")
    @pytest.mark.parametrize(
        "invalid_email",
        [
            "invalid-email",  # без @
            "test@",  # без домена
            "@domain.com",  # без имени
            "test..test@domain.com",  # двойные точки
            "test@domain",  # без TLD
            "test.@domain.com",  # точка перед @
        ],
    )
    def test_register_invalid_email(self, api_client, invalid_email) -> None:
        """Тест регистрации с невалидным email"""
        register_data = {"email": invalid_email, "password": "testpass"}

        response = api_client.post("/api/register", json=register_data)
        api.check_email_error_response(
            response, "/api/register", "Invalid email format"
        )
        logger.info(f"Registration correctly failed for invalid email: {invalid_email}")

    @allure.title("Login with invalid email formats")
    @pytest.mark.parametrize(
        "invalid_email",
        [
            "invalid-email",
            "test@",
            "@domain.com",
            "test..test@domain.com",
        ],
    )
    def test_login_invalid_email(self, api_client, invalid_email) -> None:
        """Тест логина с невалидным email"""
        login_data = {"email": invalid_email, "password": "testpass"}

        response = api_client.post("/api/login", json=login_data)
        api.check_email_error_response(response, "/api/login", "Invalid email format")
        logger.info(f"Login correctly failed for invalid email: {invalid_email}")

    @allure.title("Register without email field")
    def test_register_missing_email(self, api_client) -> None:
        """Тест регистрации без email"""
        register_data = {
            "password": "testpass"
            # email отсутствует
        }

        response = api_client.post("/api/register", json=register_data)
        api.log_and_check_status(
            response, "/api/register", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info("Registration correctly failed for missing email")

    @allure.title("Register with empty email")
    def test_register_empty_email(self, api_client) -> None:
        """Тест регистрации с пустым email"""
        register_data = {"email": "", "password": "testpass"}  # пустая строка

        response = api_client.post("/api/register", json=register_data)
        api.check_email_error_response(response, "/api/register", "Missing email")
        logger.info("Registration correctly failed for empty email")

    @allure.title("Login without email field")
    def test_login_missing_email(self, api_client) -> None:
        """Тест логина без email"""
        login_data = {
            "password": "testpass"
            # email отсутствует
        }

        response = api_client.post("/api/login", json=login_data)
        api.log_and_check_status(
            response, "/api/login", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info("Login correctly failed for missing email")

    @allure.title("Login with empty email")
    def test_login_empty_email(self, api_client) -> None:
        """Тест логина с пустым email"""
        login_data = {"email": "", "password": "testpass"}  # пустая строка

        response = api_client.post("/api/login", json=login_data)
        api.check_email_error_response(response, "/api/login", "Missing email")
        logger.info("Login correctly failed for empty email")

    @allure.title("Register without password field")
    def test_register_unsuccessful(self, api_client) -> None:
        """Тест неуспешной регистрации"""
        register_data = {
            "email": "valid@email.com",  # Валидный email
            # Пароль отсутствует
        }

        response = api_client.post("/api/register", json=register_data)
        api.log_and_check_status(
            response, "/api/register", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info("Registration failed as expected (missing password)")

    @allure.title("Login without password field")
    def test_login_unsuccessful(self, api_client) -> None:
        """Тест неуспешного логина"""
        login_data = {
            "email": "valid@email.com",  # Валидный email
            # Пароль отсутствует
        }

        response = api_client.post("/api/login", json=login_data)
        api.log_and_check_status(
            response, "/api/login", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info("Login failed as expected (missing password)")
