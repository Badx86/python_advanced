import logging
import pytest
import random
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
        user_data = generate_random_user()
        logger.info(f"Creating user with data: {user_data}")

        response = api_client.post("/api/users", json=user_data)
        api.check_create_user_response(
            response, "/api/users", user_data["name"], user_data["job"]
        )
        logger.info("User created successfully")

    def test_read_user(self, api_client) -> None:
        """Тест чтения случайного пользователя"""
        # Получаем список пользователей
        response = api_client.get("/api/users", params={"page": 1, "per_page": 50})
        users_page = api.check_users_list_response(
            response, "/api/users", page=1, per_page=50
        )

        if users_page.items:
            # Выбираем случайного пользователя из списка
            random_user = random.choice(users_page.items)
            user_id = random_user.id

            # Читаем этого случайного пользователя
            response = api_client.get(f"/api/users/{user_id}")
            api.check_user_response(response, f"/api/users/{user_id}")
            logger.info(f"Random user {user_id} read successfully")
        else:
            logger.warning("No users found in database for read test")

    def test_update_user_put(self, api_client) -> None:
        """Тест полного обновления пользователя"""
        # Создаем пользователя
        user_data = generate_random_user()
        create_response = api_client.post("/api/users", json=user_data)
        created_user = api.check_create_user_response(
            create_response, "/api/users", user_data["name"], user_data["job"]
        )
        user_id = int(created_user.id)

        # Обновляем его
        updated_data = generate_random_user()
        logger.info(f"Updating user {user_id} with data: {updated_data}")

        response = api_client.put(f"/api/users/{user_id}", json=updated_data)
        api.check_update_user_response(
            response, f"/api/users/{user_id}", updated_data["name"], updated_data["job"]
        )
        logger.info(f"User {user_id} updated successfully with PUT")

    def test_update_user_patch(self, api_client) -> None:
        """Тест частичного обновления пользователя"""
        # Создаем пользователя
        user_data = generate_random_user()
        create_response = api_client.post("/api/users", json=user_data)
        created_user = api.check_create_user_response(
            create_response, "/api/users", user_data["name"], user_data["job"]
        )
        user_id = int(created_user.id)

        # Обновляем его
        updated_data = generate_random_user()
        logger.info(f"Patching user {user_id} with data: {updated_data}")

        response = api_client.patch(f"/api/users/{user_id}", json=updated_data)
        api.check_update_user_response(
            response, f"/api/users/{user_id}", updated_data["name"], updated_data["job"]
        )
        logger.info(f"User {user_id} updated successfully with PATCH")

    def test_delete_user(self, api_client) -> None:
        """Тест удаления пользователя"""
        # Создаем пользователя
        user_data = generate_random_user()
        create_response = api_client.post("/api/users", json=user_data)
        created_user = api.check_create_user_response(
            create_response, "/api/users", user_data["name"], user_data["job"]
        )
        user_id = int(created_user.id)

        # Удаляем его
        response = api_client.delete(f"/api/users/{user_id}")
        api.check_delete_user_response(response, f"/api/users/{user_id}")
        logger.info(f"User {user_id} deleted successfully")

    def test_update_nonexistent_user(self, api_client) -> None:
        """Тест обновления несуществующего пользователя"""
        updated_data = generate_random_user()
        logger.info(f"Updating non-existent user with data: {updated_data}")

        response = api_client.put("/api/users/999999", json=updated_data)
        api.check_404_error(response, "/api/users/999999")
        logger.info("Non-existent user correctly failed with 404")

    def test_create_and_delete_flow(self, api_client) -> None:
        """Тест полного цикла: создание -> проверка -> удаление"""
        # Создаем пользователя
        user_data = generate_random_user()
        create_response = api_client.post("/api/users", json=user_data)
        created_user = api.check_create_user_response(
            create_response, "/api/users", user_data["name"], user_data["job"]
        )
        user_id = int(created_user.id)

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
