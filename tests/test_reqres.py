import logging
import pytest
from mimesis import Person
from tests.assertions import api

logger = logging.getLogger(__name__)

# Инициализируем генератор
person = Person()


def generate_random_user():
    """Генерирует случайные тестовые данные пользователя с помощью mimesis"""
    return {"name": person.first_name().lower(), "job": person.occupation().lower()}


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


class TestResources:
    """Тесты для ресурсов"""

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

    def test_resources_page_2(self, api_client) -> None:
        """Тест второй страницы ресурсов"""
        response = api_client.get("/api/unknown", params={"page": 2, "per_page": 6})
        resources_response = api.check_resources_list_response(
            response, "/api/unknown?page=2", page=2
        )

        api.check_multiple_fields(resources_response.items[0], id=7, name="sand dollar")
        logger.info("Page 2 resources work, schema valid")


class TestCRUD:
    """Тесты для создания, обновления, удаления"""

    def test_create_user(self, api_client) -> None:
        """Тест создания пользователя"""
        user_data = generate_random_user()  # Используем mimesis
        logger.info(f"Creating user with data: {user_data}")

        response = api_client.post("/api/users", json=user_data)
        api.check_create_user_response(
            response, "/api/users", user_data["name"], user_data["job"]
        )
        logger.info("User created successfully")

    def test_update_user_put(self, api_client) -> None:
        """Тест полного обновления пользователя"""
        updated_data = generate_random_user()
        logger.info(f"Updating user with data: {updated_data}")

        response = api_client.put("/api/users/2", json=updated_data)
        api.check_update_user_response(
            response, "/api/users/2", updated_data["name"], updated_data["job"]
        )
        logger.info("User updated successfully with PUT")

    def test_update_user_patch(self, api_client) -> None:
        """Тест частичного обновления пользователя"""
        updated_data = generate_random_user()
        logger.info(f"Patching user with data: {updated_data}")

        response = api_client.patch("/api/users/2", json=updated_data)
        api.check_update_user_response(
            response, "/api/users/2", updated_data["name"], updated_data["job"]
        )
        logger.info("User updated successfully with PATCH")

    def test_delete_user(self, api_client) -> None:
        """Тест удаления пользователя"""
        response = api_client.delete("/api/users/2")
        api.check_delete_user_response(response, "/api/users/2")
        logger.info("User deleted successfully")

    def test_update_nonexistent_user(self, api_client) -> None:
        """Тест обновления несуществующего пользователя"""
        updated_data = generate_random_user()
        logger.info(f"Updating non-existent user with data: {updated_data}")

        response = api_client.put("/api/users/999", json=updated_data)
        api.check_update_user_response(
            response, "/api/users/999", updated_data["name"], updated_data["job"]
        )
        logger.info("Non-existent user 'updated' successfully (as in reqres)")


class TestAuth:
    """Тесты для аутентификации"""

    def test_register_successful(self) -> None:
        """Тест успешной регистрации"""
        # POST /api/register
        pass

    def test_register_unsuccessful(self) -> None:
        """Тест неуспешной регистрации"""
        # POST /api/register (без пароля)
        pass

    def test_login_successful(self) -> None:
        """Тест успешного логина"""
        # POST /api/login
        pass

    def test_login_unsuccessful(self) -> None:
        """Тест неуспешного логина"""
        # POST /api/login (невалидные данные)
        pass


class TestSpecial:
    """Специальные тесты"""

    def test_delayed_response(self) -> None:
        """Тест задержанного ответа"""
        # GET /api/users?delay=3
        pass
