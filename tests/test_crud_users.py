import allure
import logging
import pytest
import random
from mimesis import Person
from tests.assertions import APIAssertions

logger = logging.getLogger(__name__)

# Инициализируем генератор
person = Person()


def generate_random_user():
    """Генерирует случайные тестовые данные пользователя с помощью mimesis"""
    return {"name": person.first_name().lower(), "job": person.occupation().lower()}


@allure.feature("Users CRUD Operations")
@pytest.mark.crud
class TestUsersCRUD:
    """Тесты для создания, обновления, удаления с проверкой БД"""

    @allure.title("Create new user via API")
    def test_create_user(self, api_client) -> None:
        """Тест создания пользователя (API + БД)"""
        user_info = generate_random_user()
        logger.info(f"Creating user with data: {user_info}")

        response = api_client.post("/api/users", json=user_info)

        # Логируем curl для документации создания пользователя
        APIAssertions.log_curl_command(response, "📝 Create User")

        APIAssertions.check_create_user_response(
            response, "/api/users", user_info["name"], user_info["job"]
        )
        logger.info("User created and verified in database successfully")

    @allure.title("Read existing user by ID")
    def test_read_user(self, api_client) -> None:
        """Тест чтения случайного пользователя"""
        # Получаем список пользователей
        response = api_client.get("/api/users", params={"page": 1, "size": 50})
        users_page = APIAssertions.check_users_list_response(
            response, "/api/users", page=1, per_page=50
        )

        if users_page.items:
            random_user = random.choice(users_page.items)
            user_id = random_user.id

            # Читаем этого случайного пользователя
            response = api_client.get(f"/api/users/{user_id}")
            APIAssertions.check_user_response(response, f"/api/users/{user_id}")
            logger.info(f"Random user {user_id} read successfully")
        else:
            logger.warning("No users found in database for read test")

    @allure.title("Update user with PUT method")
    def test_update_user_put(self, api_client) -> None:
        """Тест полного обновления пользователя (API + БД)"""
        user_info = generate_random_user()

        # Создаем пользователя
        create_response = api_client.post("/api/users", json=user_info)
        created_user = APIAssertions.check_create_user_response(
            create_response, "/api/users", user_info["name"], user_info["job"]
        )
        user_id = int(created_user.id)

        # Получаем исходные данные из БД для проверки
        original_user = APIAssertions.check_user_in_database(user_id)

        # Обновляем его
        updated_info = generate_random_user()
        logger.info(f"Updating user {user_id} with data: {updated_info}")

        response = api_client.put(f"/api/users/{user_id}", json=updated_info)

        # Логируем curl для документации обновления пользователя
        APIAssertions.log_curl_command(response, f"🔄 Update User {user_id}")

        APIAssertions.check_update_user_response(
            response,
            f"/api/users/{user_id}",
            updated_info["name"],
            updated_info["job"],
            user_id,
            original_user,
        )
        logger.info(f"User {user_id} updated and verified in database successfully")

    @allure.title("Update user with PATCH method")
    def test_update_user_patch(self, api_client) -> None:
        """Тест частичного обновления пользователя (API + БД)"""
        user_info = generate_random_user()

        # Создаем пользователя
        create_response = api_client.post("/api/users", json=user_info)
        created_user = APIAssertions.check_create_user_response(
            create_response, "/api/users", user_info["name"], user_info["job"]
        )
        user_id = int(created_user.id)

        # Получаем исходные данные из БД
        original_user = APIAssertions.check_user_in_database(user_id)

        # Обновляем его
        updated_info = generate_random_user()
        logger.info(f"Patching user {user_id} with data: {updated_info}")

        response = api_client.patch(f"/api/users/{user_id}", json=updated_info)
        APIAssertions.check_update_user_response(
            response,
            f"/api/users/{user_id}",
            updated_info["name"],
            updated_info["job"],
            user_id,
            original_user,
        )
        logger.info(f"User {user_id} patched and verified in database successfully")

    @allure.title("Delete user from system")
    def test_delete_user(self, api_client) -> None:
        """Тест удаления пользователя (API + БД)"""
        user_info = generate_random_user()

        # Создаем пользователя
        create_response = api_client.post("/api/users", json=user_info)
        created_user = APIAssertions.check_create_user_response(
            create_response, "/api/users", user_info["name"], user_info["job"]
        )
        user_id = int(created_user.id)

        # Удаляем его
        response = api_client.delete(f"/api/users/{user_id}")

        # Логируем curl для документации удаления пользователя
        APIAssertions.log_curl_command(response, f"🗑️ Delete User {user_id}")

        APIAssertions.check_delete_user_response(
            response, f"/api/users/{user_id}", user_id
        )
        logger.info(f"User {user_id} deleted and verified removed from database")

    @allure.title("Update non-existent user")
    def test_update_nonexistent_user(self, api_client) -> None:
        """Тест обновления несуществующего пользователя"""
        updated_info = generate_random_user()
        logger.info(f"Updating non-existent user with data: {updated_info}")

        response = api_client.put("/api/users/999999", json=updated_info)
        # curl автоматически появится при ошибке 404
        APIAssertions.check_404_error(response, "/api/users/999999")
        logger.info("Non-existent user correctly failed with 404")

    @allure.title("Delete non-existent user")
    def test_delete_nonexistent_user(self, api_client) -> None:
        """Тест удаления несуществующего пользователя"""
        response = api_client.delete("/api/users/999999")
        # curl автоматически появится при ошибке 404
        APIAssertions.check_404_error(response, "/api/users/999999")
        logger.info("Non-existent user DELETE correctly failed with 404")

    @allure.title("Full CRUD cycle for user")
    def test_create_and_delete_flow(self, api_client) -> None:
        """Тест полного цикла: создание -> проверка -> удаление (с БД проверками)"""
        user_info = generate_random_user()

        # Создаем пользователя
        create_response = api_client.post("/api/users", json=user_info)
        created_user = APIAssertions.check_create_user_response(
            create_response, "/api/users", user_info["name"], user_info["job"]
        )
        user_id = int(created_user.id)

        # Проверяем что пользователь существует в БД
        APIAssertions.check_user_in_database(user_id, user_info["name"])

        # Проверяем что пользователь доступен через API
        get_response = api_client.get(f"/api/users/{user_id}")
        APIAssertions.check_user_response(get_response, f"/api/users/{user_id}")

        # Удаляем пользователя
        delete_response = api_client.delete(f"/api/users/{user_id}")
        APIAssertions.check_delete_user_response(
            delete_response, f"/api/users/{user_id}", user_id
        )

        # Проверяем что пользователь удален из API
        get_after_delete = api_client.get(f"/api/users/{user_id}")
        # curl автоматически появится при ошибке 404
        APIAssertions.check_404_error(get_after_delete, f"/api/users/{user_id}")

        logger.info(
            f"Full CRUD cycle with database verification completed for user {user_id}"
        )
