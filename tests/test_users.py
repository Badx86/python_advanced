import allure
import logging
import pytest
from http import HTTPStatus
from tests.assertions import api

logger = logging.getLogger(__name__)


@allure.epic("API Endpoint Testing")
@allure.feature("User API Endpoints")
class TestUsers:
    """Тесты для пользователей"""

    @allure.story("User List Pagination")
    @allure.title("Get users list - first page")
    @allure.description(
        "Test retrieving first page of users with pagination parameters"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "pagination", "users", "list")
    @pytest.mark.pagination
    def test_list_users_page_1(self, api_client) -> None:
        """Тест первой страницы"""
        response = api_client.get("/api/users", params={"page": 1, "per_page": 6})
        users_page = api.check_users_list_response(
            response, "/api/users?page=1", page=1, per_page=6
        )

        logger.info(
            f"Page 1 works, got {len(users_page.items)} users, total: {users_page.total}"
        )

    @allure.story("User List Pagination")
    @allure.title("Get users list - second page")
    @allure.description(
        "Test retrieving second page of users with pagination parameters"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "pagination", "users", "list")
    @pytest.mark.pagination
    def test_list_users_page_2(self, api_client) -> None:
        """Тест второй страницы"""
        response = api_client.get("/api/users", params={"page": 2, "per_page": 6})
        users_page = api.check_users_list_response(
            response, "/api/users?page=2", page=2, per_page=6
        )

        logger.info(f"Page 2 works, got {len(users_page.items)} users")

    @allure.story("Data Integrity")
    @allure.title("Verify unique user IDs")
    @allure.description("Test that all user IDs in the list are unique - no duplicates")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "data-integrity", "users", "validation")
    def test_users_no_duplicates(self, api_client) -> None:
        """Тест уникальности ID пользователей"""
        response = api_client.get("/api/users", params={"page": 1, "per_page": 12})
        users_page = api.check_users_list_response(
            response, "/api/users", page=1, per_page=12
        )

        # Проверяем уникальность ID
        api.check_unique_ids(users_page.items, "user")
        logger.info(f"All {len(users_page.items)} user IDs are unique")

    @allure.story("Single User Retrieval")
    @allure.title("Get single user by ID")
    @allure.description("Test retrieving a single user by ID after creating them first")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "users", "single", "read")
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

    @allure.story("Error Handling")
    @allure.title("Get non-existent user by ID")
    @allure.description("Test retrieving users with non-existent IDs should return 404")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("api", "error-handling", "404", "users")
    @pytest.mark.parametrize("user_id", [1000000, 999999, 888888])
    def test_single_user_not_found(self, api_client, user_id) -> None:
        """Тест получения несуществующего пользователя"""
        response = api_client.get(f"/api/users/{user_id}")
        api.check_404_error(response, f"/api/users/{user_id}")
        logger.info(f"User {user_id} not found (404)")

    @allure.story("Input Validation")
    @allure.title("Get user with invalid ID")
    @allure.description(
        "Test retrieving users with invalid IDs (negative, zero) should return 422"
    )
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("api", "validation", "422", "users", "negative")
    @pytest.mark.parametrize("user_id", [0, -1, -999])
    def test_single_user_invalid_id(self, api_client, user_id) -> None:
        """Тест невалидного ID пользователя"""
        response = api_client.get(f"/api/users/{user_id}")
        api.log_and_check_status(
            response, f"/api/users/{user_id}", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info(f"Invalid user ID {user_id} correctly rejected (422)")

    @allure.story("Dynamic User Retrieval")
    @allure.title("Get any existing user from list")
    @allure.description(
        "Test retrieving any existing user by selecting one from the users list"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "users", "dynamic", "read")
    def test_dynamic_user_exists(self, api_client) -> None:
        """Тест получения любого существующего пользователя"""
        # Получаем список пользователей
        response = api_client.get("/api/users", params={"page": 1, "per_page": 1})
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
