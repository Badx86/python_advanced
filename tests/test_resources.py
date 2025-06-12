import pytest
import logging
from tests.assertions import api

logger = logging.getLogger(__name__)


class TestResources:
    """Тесты для ресурсов"""

    @pytest.mark.pagination
    def test_list_resources(self, api_client) -> None:
        """Тест списка ресурсов"""
        response = api_client.get("/api/unknown", params={"page": 1, "per_page": 6})
        resources_response = api.check_resources_list_response(response, "/api/unknown")

        api.check_multiple_fields(
            resources_response.items[0], name="cerulean", year=2000
        )
        logger.info("Resources list works, schema valid")

    def test_single_resource(self, api_client) -> None:
        """Тест получения одного ресурса"""
        response = api_client.get("/api/unknown/2")
        api.check_resource_response(response, "/api/unknown/2")
        logger.info("Resource 2 found, schema valid")

    def test_single_resource_not_found(self, api_client) -> None:
        """Тест получения несуществующего ресурса"""
        response = api_client.get("/api/unknown/23")
        api.check_404_error(response, "/api/unknown/23")
        logger.info("Resource 23 not found (404)")

    @pytest.mark.pagination
    def test_resources_page_2(self, api_client) -> None:
        """Тест второй страницы ресурсов"""
        response = api_client.get("/api/unknown", params={"page": 2, "per_page": 6})
        resources_response = api.check_resources_list_response(
            response, "/api/unknown?page=2", page=2
        )

        api.check_multiple_fields(resources_response.items[0], id=7, name="sand dollar")
        logger.info("Page 2 resources work, schema valid")
