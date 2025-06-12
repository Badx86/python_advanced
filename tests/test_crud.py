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
