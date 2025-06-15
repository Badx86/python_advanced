import logging
import pytest
from http import HTTPStatus
from tests.assertions import api

logger = logging.getLogger(__name__)


class TestUsers:
    """Тесты для пользователей"""

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

    @pytest.mark.pagination
    def test_list_users_page_2(self, api_client) -> None:
        """Тест второй страницы"""
        response = api_client.get("/api/users", params={"page": 2, "per_page": 6})
        users_page = api.check_users_list_response(
            response, "/api/users?page=2", page=2, per_page=6
        )

        logger.info(f"Page 2 works, got {len(users_page.items)} users")

    def test_users_no_duplicates(self, api_client) -> None:
        """Тест уникальности ID пользователей"""
        response = api_client.get("/api/users", params={"page": 1, "per_page": 12})
        users_page = api.check_users_list_response(
            response, "/api/users", page=1, per_page=12
        )

        # Проверяем уникальность ID
        api.check_unique_ids(users_page.items, "user")
        logger.info(f"All {len(users_page.items)} user IDs are unique")

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

    @pytest.mark.parametrize("user_id", [1000000, 999999, 888888])
    def test_single_user_not_found(self, api_client, user_id) -> None:
        """Тест получения несуществующего пользователя"""
        response = api_client.get(f"/api/users/{user_id}")
        api.check_404_error(response, f"/api/users/{user_id}")
        logger.info(f"User {user_id} not found (404)")

    @pytest.mark.parametrize("user_id", [0, -1, -999])
    def test_single_user_invalid_id(self, api_client, user_id) -> None:
        """Тест невалидного ID пользователя"""
        response = api_client.get(f"/api/users/{user_id}")
        api.log_and_check_status(
            response, f"/api/users/{user_id}", HTTPStatus.UNPROCESSABLE_ENTITY
        )
        logger.info(f"Invalid user ID {user_id} correctly rejected (422)")

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
