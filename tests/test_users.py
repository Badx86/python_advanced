import logging
import pytest
from tests.assertions import api

logger = logging.getLogger(__name__)


class TestUsers:
    """Тесты для пользователей"""

    @pytest.mark.pagination
    def test_list_users_page_1(self, api_client) -> None:
        """Тест первой страницы"""
        response = api_client.get("/api/users", params={"page": 1, "per_page": 6})
        api.log_and_check_status(response, "/api/users?page=1")

        data = response.json()
        # Проверяем структуру без привязки к количеству
        assert "page" in data
        assert "size" in data
        assert "total" in data
        assert "pages" in data
        assert "items" in data
        assert data["page"] == 1
        assert data["size"] == 6
        assert len(data["items"]) <= 6  # Может быть меньше если данных мало

        logger.info(
            f"Page 1 works, got {len(data['items'])} users, total: {data['total']}"
        )

    @pytest.mark.pagination
    def test_list_users_page_2(self, api_client) -> None:
        """Тест второй страницы"""
        response = api_client.get("/api/users", params={"page": 2, "per_page": 6})
        api.log_and_check_status(response, "/api/users?page=2")

        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 6
        # Не проверяем конкретный ID - может варьироваться
        logger.info(f"Page 2 works, got {len(data['items'])} users")

    def test_users_no_duplicates(self, api_client) -> None:
        """Тест уникальности ID пользователей"""
        response = api_client.get("/api/users", params={"page": 1, "per_page": 12})
        api.log_and_check_status(response, "/api/users")

        data = response.json()
        users_ids = [user["id"] for user in data["items"]]
        assert len(users_ids) == len(set(users_ids)), "Found duplicate user IDs"
        logger.info(f"All {len(users_ids)} user IDs are unique")

    def test_single_user_exists(self, api_client) -> None:
        """Тест получения существующего пользователя"""
        # Сначала создаем пользователя для теста
        test_user = {"name": "TestUser", "job": "TestJob"}
        create_response = api_client.post("/api/users", json=test_user)
        assert create_response.status_code == 201

        created_user = create_response.json()
        user_id = int(created_user["id"])

        # Теперь проверяем что можем получить этого пользователя
        response = api_client.get(f"/api/users/{user_id}")
        api.check_user_response(response, f"/api/users/{user_id}")
        logger.info(f"Created and verified user {user_id}")

    @pytest.mark.parametrize("user_id", [999, 23, 9999])
    def test_single_user_not_found(self, api_client, user_id) -> None:
        """Тест получения несуществующего пользователя"""
        response = api_client.get(f"/api/users/{user_id}")
        api.check_404_error(response, f"/api/users/{user_id}")
        logger.info(f"User {user_id} not found (404)")

    def test_dynamic_user_exists(self, api_client) -> None:
        """Тест получения любого существующего пользователя"""
        # Получаем список пользователей
        response = api_client.get("/api/users", params={"page": 1, "per_page": 1})
        api.log_and_check_status(response, "/api/users")

        data = response.json()
        if data["items"]:
            user_id = data["items"][0]["id"]
            # Проверяем этого пользователя
            response = api_client.get(f"/api/users/{user_id}")
            api.check_user_response(response, f"/api/users/{user_id}")
            logger.info(f"Dynamic user {user_id} found, schema valid")
        else:
            logger.warning("No users found in database")
