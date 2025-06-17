import allure
import pytest
import logging
from tests.assertions import api

logger = logging.getLogger(__name__)


@allure.epic("Application Health & Monitoring")
@allure.feature("Service Health Checks")
@pytest.mark.smoke
class TestSmoke:
    """Smoke тесты - проверка доступности сервиса"""

    @allure.story("Service Availability")
    @allure.title("Service responds to requests")
    @allure.description(
        "Verify that the service is alive and responding to HTTP requests"
    )
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.tag("smoke", "health", "api", "availability")
    def test_service_is_alive(self, api_client) -> None:
        """Сервис отвечает на запросы"""
        response = api_client.get("/status")
        api.log_and_check_status(response, "/status")
        logger.info("Service is alive and responding")

    @allure.story("Service Status")
    @allure.title("Application status endpoint returns valid data")
    @allure.description(
        "Verify that application status endpoint returns proper health information"
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "health", "status", "database")
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

    @allure.story("Endpoint Accessibility")
    @allure.title("Main endpoints are accessible")
    @allure.description(
        "Verify that main API endpoints are accessible and return valid responses"
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "endpoints", "accessibility")
    def test_main_endpoints_accessible(self, api_client) -> None:
        """Основные эндпоинты доступны"""
        endpoints = ["/api/users", "/api/unknown"]

        for endpoint in endpoints:
            response = api_client.get(endpoint)
            api.log_and_check_status(response, endpoint)
            logger.info(f"Endpoint {endpoint} is accessible")

    @allure.story("Data Structure")
    @allure.title("Service returns valid data structure")
    @allure.description(
        "Verify that service returns properly formatted data with correct structure"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("smoke", "data-structure", "validation")
    def test_service_info(self, api_client) -> None:
        """Сервис возвращает корректную информацию"""
        response = api_client.get("/api/users", params={"per_page": 1})
        api.log_and_check_status(response, "/api/users")

        data = response.json()
        assert "items" in data, "Response structure is invalid"
        assert "total" in data, "Pagination info missing"
        logger.info("Service returns valid data structure")
