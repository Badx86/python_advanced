import logging
import pytest
from tests.assertions import api

logger = logging.getLogger(__name__)


class TestAuth:
    """Тесты для аутентификации"""

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "invalid-email",  # без @
            "test@",  # без домена
            "@domain.com",  # без имени
            "test..test@domain.com",  # двойные точки
            "   ",  # пробелы
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

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "invalid-email",
            "test@",
            "@domain.com",
            "test..test@domain.com",
            "   ",  # пробелы
        ],
    )
    def test_login_invalid_email(self, api_client, invalid_email) -> None:
        """Тест логина с невалидным email"""
        login_data = {"email": invalid_email, "password": "testpass"}

        response = api_client.post("/api/login", json=login_data)
        api.check_email_error_response(response, "/api/login", "Invalid email format")
        logger.info(f"Login correctly failed for invalid email: {invalid_email}")

    def test_register_missing_email(self, api_client) -> None:
        """Тест регистрации без email"""
        register_data = {
            "password": "testpass"
            # email отсутствует
        }

        response = api_client.post("/api/register", json=register_data)
        api.check_email_error_response(response, "/api/register", "Missing email")
        logger.info("Registration correctly failed for missing email")

    def test_register_empty_email(self, api_client) -> None:
        """Тест регистрации с пустым email"""
        register_data = {"email": "", "password": "testpass"}  # пустая строка

        response = api_client.post("/api/register", json=register_data)
        api.check_email_error_response(response, "/api/register", "Missing email")
        logger.info("Registration correctly failed for empty email")

    def test_login_missing_email(self, api_client) -> None:
        """Тест логина без email"""
        login_data = {
            "password": "testpass"
            # email отсутствует
        }

        response = api_client.post("/api/login", json=login_data)
        api.check_email_error_response(response, "/api/login", "Missing email")
        logger.info("Login correctly failed for missing email")

    def test_login_empty_email(self, api_client) -> None:
        """Тест логина с пустым email"""
        login_data = {"email": "", "password": "testpass"}  # пустая строка

        response = api_client.post("/api/login", json=login_data)
        api.check_email_error_response(response, "/api/login", "Missing email")
        logger.info("Login correctly failed for empty email")

    def test_register_unsuccessful(self, api_client) -> None:
        """Тест неуспешной регистрации"""
        register_data = {
            "email": "valid@email.com",  # Валидный email
            # Пароль отсутствует
        }

        response = api_client.post("/api/register", json=register_data)
        api.check_email_error_response(response, "/api/register", "Missing password")
        logger.info("Registration failed as expected (missing password)")

    def test_login_unsuccessful(self, api_client) -> None:
        """Тест неуспешного логина"""
        login_data = {
            "email": "valid@email.com",  # Валидный email
            # Пароль отсутствует
        }

        response = api_client.post("/api/login", json=login_data)
        api.check_email_error_response(response, "/api/login", "Missing password")
        logger.info("Login failed as expected (missing password)")
