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


@pytest.mark.crud
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

        test_id = 9001
        response = api_client.put(f"/api/users/{test_id}", json=updated_data)
        api.check_update_user_response(
            response, f"/api/users/{test_id}", updated_data["name"], updated_data["job"]
        )
        logger.info(f"User {test_id} updated successfully with PUT")

    def test_update_user_patch(self, api_client) -> None:
        """Тест частичного обновления пользователя"""
        updated_data = generate_random_user()
        logger.info(f"Patching user with data: {updated_data}")

        test_id = 9002
        response = api_client.patch(f"/api/users/{test_id}", json=updated_data)
        api.check_update_user_response(
            response, f"/api/users/{test_id}", updated_data["name"], updated_data["job"]
        )
        logger.info(f"User {test_id} updated successfully with PATCH")

    def test_delete_user(self, api_client) -> None:
        """Тест удаления пользователя"""
        # Используем высокий ID чтобы не удалить реальных пользователей
        test_id = 9003
        response = api_client.delete(f"/api/users/{test_id}")
        api.check_delete_user_response(response, f"/api/users/{test_id}")
        logger.info(f"User {test_id} deleted successfully")

    def test_update_nonexistent_user(self, api_client) -> None:
        """Тест обновления несуществующего пользователя"""
        updated_data = generate_random_user()
        logger.info(f"Updating non-existent user with data: {updated_data}")

        response = api_client.put("/api/users/999999", json=updated_data)
        api.check_update_user_response(
            response, "/api/users/999999", updated_data["name"], updated_data["job"]
        )
        logger.info("Non-existent user 'updated' successfully (as in reqres)")

    def test_create_and_delete_flow(self, api_client) -> None:
        """Тест полного цикла: создание -> проверка -> удаление"""
        # Создаем пользователя
        user_data = generate_random_user()
        create_response = api_client.post("/api/users", json=user_data)
        assert create_response.status_code == 201

        created_user = create_response.json()
        user_id = int(created_user["id"])

        # Проверяем что пользователь существует
        get_response = api_client.get(f"/api/users/{user_id}")
        api.check_user_response(get_response, f"/api/users/{user_id}")

        # Удаляем пользователя
        delete_response = api_client.delete(f"/api/users/{user_id}")
        api.check_delete_user_response(delete_response, f"/api/users/{user_id}")

        # Проверяем что пользователь удален
        get_after_delete = api_client.get(f"/api/users/{user_id}")
        api.check_404_error(get_after_delete, f"/api/users/{user_id}")

        logger.info(f"Full CRUD cycle completed for user {user_id}")
