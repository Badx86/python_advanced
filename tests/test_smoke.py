import allure
import pytest
import logging
from tests.assertions import APIAssertions

logger = logging.getLogger(__name__)


@allure.feature("Service Health Check")
@pytest.mark.smoke
class TestSmoke:
    """Smoke тесты - проверка доступности сервиса"""

    @allure.title("Service responds to requests")
    def test_service_is_alive(self, api_client) -> None:
        """Сервис отвечает на запросы"""
        response = api_client.get("/status")
        APIAssertions.log_and_check_status(response, "/status")
        logger.info("Service is alive and responding")

    @allure.title("Application status endpoint returns valid data")
    def test_app_status(self, api_client) -> None:
        """Проверка статуса приложения"""
        response = api_client.get("/status")
        APIAssertions.log_and_check_status(response, "/status")

        status = response.json()

        assert status["status"] in ["healthy", "unhealthy"], "Invalid status value"
        assert status["data"]["users"]["loaded"] is True, "Users data not loaded"
        assert (
            status["data"]["resources"]["loaded"] is True
        ), "Resources data not loaded"
        logger.info("All application data loaded successfully")

    @allure.title("Main endpoints are accessible")
    def test_main_endpoints_accessible(self, api_client) -> None:
        """Основные эндпоинты доступны"""
        endpoints = ["/api/users", "/api/resources"]

        for endpoint in endpoints:
            response = api_client.get(endpoint)
            APIAssertions.log_and_check_status(response, endpoint)
            logger.info(f"Endpoint {endpoint} is accessible")

    @allure.title("Service returns valid data structure")
    def test_service_info(self, api_client) -> None:
        """Сервис возвращает корректную информацию"""
        response = api_client.get("/api/users", params={"size": 1})
        APIAssertions.log_and_check_status(response, "/api/users")

        data = response.json()
        assert "items" in data, "Response structure is invalid"
        assert "total" in data, "Pagination info missing"
        logger.info("Service returns valid data structure")
