import allure
import pytest
import logging
from tests.assertions import api

logger = logging.getLogger(__name__)


@allure.epic("API Endpoint Testing")
@allure.feature("Resource API Endpoints")
class TestResources:
    """Тесты для ресурсов"""

    @allure.story("Resource List Pagination")
    @allure.title("Get resources list with pagination")
    @allure.description(
        "Test retrieving paginated list of resources and verify response structure"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "pagination", "resources", "list")
    @pytest.mark.pagination
    def test_list_resources(self, api_client) -> None:
        """Тест списка ресурсов"""
        response = api_client.get("/api/unknown", params={"page": 1, "size": 6})
        resources_response = api.check_resources_list_response(response, "/api/unknown")

        api.check_multiple_fields(
            resources_response.items[0], name="cerulean", year=2000
        )
        logger.info("Resources list works, schema valid")

    @allure.story("Single Resource Retrieval")
    @allure.title("Get single resource by ID")
    @allure.description(
        "Test retrieving a single resource by ID and verify response structure"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "resources", "single", "read")
    def test_single_resource(self, api_client) -> None:
        """Тест получения одного ресурса"""
        response = api_client.get("/api/unknown/2")
        api.check_resource_response(response, "/api/unknown/2")
        logger.info("Resource 2 found, schema valid")

    @allure.story("Error Handling")
    @allure.title("Get non-existent resource by ID")
    @allure.description(
        "Test retrieving resources with non-existent IDs should return 404"
    )
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("api", "error-handling", "404", "resources")
    @pytest.mark.parametrize("resource_id", [999999, 888888, 777777])
    def test_single_resource_not_found(self, api_client, resource_id) -> None:
        """Тест получения несуществующего ресурса"""
        response = api_client.get(f"/api/unknown/{resource_id}")
        api.check_404_error(response, f"/api/unknown/{resource_id}")
        logger.info(f"Resource {resource_id} not found (404)")

    @allure.story("Resource List Pagination")
    @allure.title("Get resources list - second page")
    @allure.description(
        "Test retrieving second page of resources with pagination parameters"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "pagination", "resources", "list")
    @pytest.mark.pagination
    def test_resources_page_2(self, api_client) -> None:
        """Тест второй страницы ресурсов"""
        response = api_client.get("/api/unknown", params={"page": 2, "size": 6})
        resources_response = api.check_resources_list_response(
            response, "/api/unknown?page=2", page=2
        )

        api.check_multiple_fields(resources_response.items[0], id=7, name="sand dollar")
        logger.info("Page 2 resources work, schema valid")

    @allure.story("Data Integrity")
    @allure.title("Verify unique resource IDs")
    @allure.description(
        "Test that all resource IDs in the list are unique - no duplicates"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "data-integrity", "resources", "validation")
    def test_resources_no_duplicates(self, api_client) -> None:
        """Тест уникальности ID ресурсов"""
        response = api_client.get("/api/unknown", params={"page": 1, "size": 12})
        resources_page = api.check_resources_list_response(
            response, "/api/unknown", page=1, per_page=12
        )

        # Проверяем уникальность ID
        api.check_unique_ids(resources_page.items, "resource")
        logger.info(f"All {len(resources_page.items)} resource IDs are unique")
