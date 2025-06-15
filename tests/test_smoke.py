import pytest
import logging
from tests.assertions import api

logger = logging.getLogger(__name__)


@pytest.mark.smoke
class TestSmoke:
    """Smoke тесты - проверка доступности сервиса"""

    def test_service_is_alive(self, api_client) -> None:
        """Сервис отвечает на запросы"""
        response = api_client.get("/status")
        api.log_and_check_status(response, "/status")
        logger.info("Service is alive and responding")

    def test_app_status(self, api_client) -> None:
        """Проверка статуса приложения"""
        response = api_client.get("/status")
        api.log_and_check_status(response, "/status")

        status = response.json()

        assert status["status"] in ["healthy", "unhealthy"], "Invalid status value"
        assert status["data"]["users"]["loaded"] is True, "Users data not loaded"
        assert (
            status["data"]["resources"]["loaded"] is True
        ), "Resources data not loaded"
        logger.info("All application data loaded successfully")

    def test_main_endpoints_accessible(self, api_client) -> None:
        """Основные эндпоинты доступны"""
        endpoints = ["/api/users", "/api/unknown"]

        for endpoint in endpoints:
            response = api_client.get(endpoint)
            api.log_and_check_status(response, endpoint)
            logger.info(f"Endpoint {endpoint} is accessible")

    def test_service_info(self, api_client) -> None:
        """Сервис возвращает корректную информацию"""
        response = api_client.get("/api/users", params={"per_page": 1})
        api.log_and_check_status(response, "/api/users")

        data = response.json()
        assert "items" in data, "Response structure is invalid"
        assert "total" in data, "Pagination info missing"
        logger.info("Service returns valid data structure")
