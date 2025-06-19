import allure
import logging
import pytest
from http import HTTPStatus
from tests.assertions import api

logger = logging.getLogger(__name__)


@allure.feature("User API Endpoints")
class TestUsers:
    """Тесты для пользователей"""

    @allure.title("Get users list - first page")
    @pytest.mark.pagination
    def test_list_users_page_1(self, api_client) -> None:
        """Тест первой страницы"""
        response = api_client.get("/api/users", params={"page": 1, "size": 6})
        users_page = api.check_users_list_response(
            response, "/api/users?page=1", page=1, per_page=6
        )

        logger.info(
            f"Page 1 works, got {len(users_page.items)} users, total: {users_page.total}"
        )

    @allure.title("Get users list - second page")
    @pytest.mark.pagination
    def test_list_users_page_2(self, api_client) -> None:
        """Тест второй страницы"""
        response = api_client.get("/api/users", params={"page": 2, "size": 6})
        users_page = api.check_users_list_response(
            response, "/api/users?page=2", page=2, per_page=6
        )

        logger.info(f"Page 2 works, got {len(users_page.items)} users")

    @allure.title("Verify unique user IDs")
    def test_users_no_duplicates(self, api_client) -> None:
        """Тест уникальности ID пользователей"""
        response = api_client.get("/api/users", params={"page": 1, "size": 12})
        users_page = api.check_users_list_response(
            response, "/api/users", page=1, per_page=12
        )

        # Проверяем уникальность ID
        api.check_unique_ids(users_page.items, "user")
        logger.info(f"All {len(users_page.items)} user IDs are unique")

    @allure.title("Get single user by ID")
    def test_single_user_exists(self, api_client) -> None:
        """Тест получения существующего пользователя"""
        # Сначала создаем пользователя для теста
        test_user = {"name": "TestUser", "job": "TestJob"}
        create_response = api_client.post("/api/users", json=test_user)
        api.check_create_user_response(
            create_response, "/api/users", test_user["name"], test_user["job"]
        )

        created_user = create_response.json()
        user_id = int(created_user["id"])

        # Теперь проверяем что можем получить этого пользователя
        response = api_client.get(f"/api/users/{user_id}")
        api.check_user_response(response, f"/api/users/{user_id}")
        logger.info(f"Created and verified user {user_id}")

    @allure.title("Get non-existent user by ID")
    @pytest.mark.parametrize("user_id", [1000000, 999999, 888888])
    def test_single_user_not_found(self, api_client, user_id) -> None:
        """Тест получения несуществующего пользователя"""
        response = api_client.get(f"/api/users/{user_id}")
        api.check_404_error(response, f"/api/users/{user_id}")
        logger.info(f"User {user_id} not found (404)")

    @allure.title("Get user with invalid ID")
    @pytest.mark.parametrize("user_id", [0, -1, -999])
    def test_single_user_invalid_id(self, api_client, user_id) -> None:
        """Тест невалидного ID пользователя"""
        response = api_client.get(f"/api/users/{user_id}")
        api.log_and_check_status(
            response, f"/api/users/{user_id}", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info(f"Invalid user ID {user_id} correctly rejected (422)")

    @allure.title("Get any existing user from list")
    def test_dynamic_user_exists(self, api_client) -> None:
        """Тест получения любого существующего пользователя"""
        # Получаем список пользователей
        response = api_client.get("/api/users", params={"page": 1, "size": 1})
        users_page = api.check_users_list_response(
            response, "/api/users", page=1, per_page=1
        )

        if users_page.items:
            user_id = users_page.items[0].id
            # Проверяем этого пользователя
            response = api_client.get(f"/api/users/{user_id}")
            api.check_user_response(response, f"/api/users/{user_id}")
            logger.info(f"Dynamic user {user_id} found, schema valid")
        else:
            logger.warning("No users found in database")

    @allure.title("Verify pagination calculations and item counts")
    @pytest.mark.pagination
    @pytest.mark.parametrize("page,size", [(1, 1), (1, 6), (2, 6), (1, 12), (1, 50)])
    def test_pagination_calculations(self, api_client, page, size) -> None:
        """Проверка корректности расчетов пагинации и количества элементов"""
        response = api_client.get("/api/users", params={"page": page, "size": size})
        users_page = api.check_users_list_response(
            response, f"/api/users?page={page}&size={size}", page=page, per_page=size
        )

        api.check_pagination_pages_calculation(users_page, size)
        api.check_pagination_items_count(users_page, page, size)

        logger.info(
            f"Pagination calculations correct: page={page}, size={size}, items={len(users_page.items)}, pages={users_page.pages}"
        )

    @allure.title("Verify different pages return different data")
    @pytest.mark.pagination
    def test_pagination_different_pages(self, api_client) -> None:
        """Проверка уникальности данных на разных страницах пагинации"""
        response = api_client.get("/api/users", params={"page": 1, "size": 6})
        first_page = api.check_users_list_response(
            response, "/api/users?page=1", page=1, per_page=6
        )

        if first_page.total > 6 and first_page.pages > 1:
            response = api_client.get("/api/users", params={"page": 2, "size": 6})
            second_page = api.check_users_list_response(
                response, "/api/users?page=2", page=2, per_page=6
            )

            api.check_pagination_different_data(
                first_page.items, second_page.items, "user"
            )
            logger.info("Different pages contain different data and unique IDs")
        else:
            logger.info("Skipped different pages test - insufficient data")

    @allure.title("Invalid pagination parameters should be rejected")
    @pytest.mark.pagination
    @pytest.mark.parametrize("page,size", [(0, 6), (-1, 6), (1, 0), (1, -5)])
    def test_pagination_invalid_parameters(self, api_client, page, size) -> None:
        """Проверка валидации параметров пагинации"""
        from http import HTTPStatus

        response = api_client.get("/api/users", params={"page": page, "size": size})
        api.log_and_check_status(
            response,
            f"/api/users?page={page}&size={size}",
            HTTPStatus.UNPROCESSABLE_ENTITY,
        )
        logger.info(f"Invalid pagination correctly rejected: page={page}, size={size}")

    @allure.title("Page beyond available returns empty results")
    @pytest.mark.pagination
    def test_pagination_beyond_available(self, api_client) -> None:
        """Проверка поведения при запросе несуществующей страницы"""
        response = api_client.get("/api/users", params={"page": 1, "size": 6})
        users_page = api.check_users_list_response(
            response, "/api/users", page=1, per_page=6
        )

        beyond_page = users_page.pages + 5
        response = api_client.get("/api/users", params={"page": beyond_page, "size": 6})
        beyond_page_response = api.check_users_list_response(
            response, f"/api/users?page={beyond_page}", page=beyond_page, per_page=6
        )

        api.check_pagination_empty_page(beyond_page_response)
        logger.info(
            f"Page {beyond_page} beyond {users_page.pages} correctly returns empty"
        )
