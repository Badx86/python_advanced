import logging
import pytest
from tests.assertions import api

logger = logging.getLogger(__name__)


class TestUsers:
    """Тесты для пользователей"""

    def test_list_users_page_1(self, api_client) -> None:
        """Тест первой страницы"""
        response = api_client.get("/api/users", params={"page": 1, "per_page": 6})
        users_response = api.check_users_list_response(response, "/api/users?page=1")

        api.check_data_count(users_response, 6)
        logger.info("Page 1 works, schema valid")

    def test_list_users_page_2(self, api_client) -> None:
        """Тест второй страницы"""
        response = api_client.get("/api/users", params={"page": 2, "per_page": 6})
        users_response = api.check_users_list_response(
            response, "/api/users?page=2", page=2
        )

        api.check_first_item_field(users_response, "id", 7)
        logger.info("Page 2 works, schema valid")

    def test_users_no_duplicates(self, api_client) -> None:
        """Тест уникальности ID пользователей"""
        response = api_client.get("/api/users", params={"page": 1, "per_page": 12})
        users_response = api.check_users_list_response(
            response, "/api/users", page=1, per_page=12
        )

        users_ids = [user.id for user in users_response.items]
        assert len(users_ids) == len(set(users_ids)), "Found duplicate user IDs"
        logger.info("All user IDs are unique")

    @pytest.mark.parametrize("user_id", [2, 7, 12])
    def test_single_user_exists(self, api_client, user_id) -> None:
        """Тест получения существующего пользователя"""
        response = api_client.get(f"/api/users/{user_id}")
        api.check_user_response(response, f"/api/users/{user_id}")
        logger.info(f"User {user_id} found, schema valid")

    @pytest.mark.parametrize("user_id", [999, 23])
    def test_single_user_not_found(self, api_client, user_id) -> None:
        """Тест получения несуществующего пользователя"""
        response = api_client.get(f"/api/users/{user_id}")
        api.check_404_error(response, f"/api/users/{user_id}")
        logger.info(f"User {user_id} not found (404)")
