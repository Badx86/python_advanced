from http import HTTPStatus
import allure
import pytest
import logging
from tests.assertions import api

logger = logging.getLogger(__name__)


@allure.feature("Resource API Endpoints")
class TestResources:
    """Тесты для ресурсов"""

    @allure.title("Get resources list with pagination")
    @pytest.mark.pagination
    def test_list_resources(self, api_client) -> None:
        """Тест списка ресурсов"""
        response = api_client.get("/api/resources", params={"page": 1, "size": 6})
        resources_response = api.check_resources_list_response(
            response, "/api/resources"
        )

        api.check_multiple_fields(
            resources_response.items[0], name="cerulean", year=2000
        )
        logger.info("Resources list works, schema valid")

    @allure.title("Get single resource by ID")
    def test_single_resource(self, api_client) -> None:
        """Тест получения одного ресурса"""
        response = api_client.get("/api/resources/2")
        api.check_resource_response(response, "/api/resources/2")
        logger.info("Resource 2 found, schema valid")

    @allure.title("Get non-existent resource by ID")
    @pytest.mark.parametrize("resource_id", [999999, 888888, 777777])
    def test_single_resource_not_found(self, api_client, resource_id) -> None:
        """Тест получения несуществующего ресурса"""
        response = api_client.get(f"/api/resources/{resource_id}")
        api.check_404_error(response, f"/api/resources/{resource_id}")
        logger.info(f"Resource {resource_id} not found (404)")

    @allure.title("Get resources list - second page")
    @pytest.mark.pagination
    def test_resources_page_2(self, api_client) -> None:
        """Тест второй страницы ресурсов"""
        response = api_client.get("/api/resources", params={"page": 2, "size": 6})
        resources_response = api.check_resources_list_response(
            response, "/api/resources?page=2", page=2
        )

        api.check_multiple_fields(resources_response.items[0], id=7, name="sand dollar")
        logger.info("Page 2 resources work, schema valid")

    @allure.title("Verify unique resource IDs")
    def test_resources_no_duplicates(self, api_client) -> None:
        """Тест уникальности ID ресурсов"""
        response = api_client.get("/api/resources", params={"page": 1, "size": 12})
        resources_page = api.check_resources_list_response(
            response, "/api/resources", page=1, per_page=12
        )

        # Проверяем уникальность ID
        api.check_unique_ids(resources_page.items, "resource")
        logger.info(f"All {len(resources_page.items)} resource IDs are unique")

    @allure.title("Verify pagination calculations and item counts")
    @pytest.mark.pagination
    @pytest.mark.parametrize("page,size", [(1, 1), (1, 6), (2, 6), (1, 12), (1, 50)])
    def test_pagination_calculations(self, api_client, page, size) -> None:
        """Проверка корректности расчетов пагинации и количества элементов"""
        response = api_client.get("/api/resources", params={"page": page, "size": size})
        resources_page = api.check_resources_list_response(
            response,
            f"/api/resources?page={page}&size={size}",
            page=page,
            per_page=size,
        )

        api.check_pagination_pages_calculation(resources_page, size)
        api.check_pagination_items_count(resources_page, page, size)

        logger.info(
            f"Pagination calculations correct: page={page}, size={size}, items={len(resources_page.items)}, pages={resources_page.pages}"
        )

    @allure.title("Verify different pages return different data")
    @pytest.mark.pagination
    def test_pagination_different_pages(self, api_client) -> None:
        """Проверка уникальности данных на различных страницах"""
        response = api_client.get("/api/resources", params={"page": 1, "size": 6})
        first_page = api.check_resources_list_response(
            response, "/api/resources?page=1", page=1, per_page=6
        )

        if first_page.total > 6 and first_page.pages > 1:
            response = api_client.get("/api/resources", params={"page": 2, "size": 6})
            second_page = api.check_resources_list_response(
                response, "/api/resources?page=2", page=2, per_page=6
            )

            api.check_pagination_different_data(
                first_page.items, second_page.items, "resource"
            )
            logger.info("Different pages contain different data and unique IDs")
        else:
            logger.info("Skipped different pages test - insufficient data")

    @allure.title("Invalid pagination parameters should be rejected")
    @pytest.mark.pagination
    @pytest.mark.parametrize("page,size", [(0, 6), (-1, 6), (1, 0), (1, -5)])
    def test_pagination_invalid_parameters(self, api_client, page, size) -> None:
        """Проверка валидации параметров пагинации"""
        response = api_client.get("/api/resources", params={"page": page, "size": size})

        api.log_and_check_status(
            response,
            f"/api/resources?page={page}&size={size}",
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )

        logger.info(f"Invalid pagination correctly rejected: page={page}, size={size}")

    @allure.title("Page beyond available returns empty results")
    @pytest.mark.pagination
    def test_pagination_beyond_available(self, api_client) -> None:
        """Проверка поведения при запросе несуществующей страницы"""
        response = api_client.get("/api/resources", params={"page": 1, "size": 6})
        resources_page = api.check_resources_list_response(
            response, "/api/resources", page=1, per_page=6
        )

        beyond_page = resources_page.pages + 5
        response = api_client.get(
            "/api/resources", params={"page": beyond_page, "size": 6}
        )
        beyond_page_response = api.check_resources_list_response(
            response, f"/api/resources?page={beyond_page}", page=beyond_page, per_page=6
        )

        api.check_pagination_empty_page(beyond_page_response)
        logger.info(
            f"Page {beyond_page} beyond {resources_page.pages} correctly returns empty"
        )
