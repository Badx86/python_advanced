import requests
import logging
from app.models import UsersListResponse, SingleUserResponse


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


class TestUsers:
    """Тесты для пользователей"""

    def test_list_users_page_1(self, api_client) -> None:
        """Тест первой страницы"""
        response = api_client.get("/api/users", params={"page": 1})
        logger.info(f"GET /api/users?page=1 - Status: {response.status_code}")

        assert response.status_code == 200

        # Парсим и валидируем через pydantic
        users_response: UsersListResponse = UsersListResponse(**response.json())

        # Работаем с типизированным объектом
        assert users_response.page == 1
        assert users_response.per_page == 6
        assert users_response.total == 12
        assert users_response.total_pages == 2
        assert len(users_response.data) == 6
        logger.info("Page 1 works, schema valid")

    def test_list_users_page_2(self) -> None:
        """Тест второй страницы"""
        response = requests.get(f"{BASE_URL}/api/users?page=2")
        logger.info(f"GET /api/users?page=2 - Status: {response.status_code}")

        assert response.status_code == 200

        users_response: UsersListResponse = UsersListResponse(**response.json())

        assert users_response.page == 2
        assert users_response.per_page == 6
        assert len(users_response.data) == 6
        assert users_response.data[0].id == 7
        logger.info("Page 2 works, schema valid")

    def test_default_params(self, api_client) -> None:
        """Тест без параметров"""
        response = api_client.get("/api/users")
        logger.info(f"GET /api/users (default) - Status: {response.status_code}")

        assert response.status_code == 200

        users_response: UsersListResponse = UsersListResponse(**response.json())

        assert users_response.page == 1
        assert users_response.per_page == 6
        logger.info("Default params work, schema valid")

    def test_single_user_exists(self, api_client) -> None:
        """Тест получения существующего пользователя"""
        response = api_client.get("/api/users/2")
        logger.info(f"GET /api/users/2 - Status: {response.status_code}")

        assert response.status_code == 200

        user_response: SingleUserResponse = SingleUserResponse(**response.json())

        assert user_response.data.id == 2
        assert user_response.data.email == "janet.weaver@reqres.in"
        assert user_response.data.first_name == "Janet"
        assert user_response.data.last_name == "Weaver"
        logger.info("User 2 found, schema valid")

    def test_single_user_not_found(self) -> None:
        """Тест получения несуществующего пользователя"""
        response = requests.get(f"{BASE_URL}/api/users/999")
        logger.info(f"GET /api/users/999 - Status: {response.status_code}")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == {}
        logger.info("User 999 not found (404)")

    def test_single_user_23_not_found(self) -> None:
        """Тест получения пользователя 23 (как в оригинальном reqres)"""
        response = requests.get(f"{BASE_URL}/api/users/23")
        logger.info(f"GET /api/users/23 - Status: {response.status_code}")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == {}
        logger.info("User 23 not found (404)")

    def test_different_users(self) -> None:
        """Тест получения разных пользователей"""
        # Первый пользователь
        response_first_user = requests.get(f"{BASE_URL}/api/users/1")
        logger.info(f"GET /api/users/1 - Status: {response_first_user.status_code}")

        assert response_first_user.status_code == 200
        user1: SingleUserResponse = SingleUserResponse(**response_first_user.json())

        assert user1.data.first_name == "George"
        assert user1.data.last_name == "Bluth"

        # Последний пользователь
        response_last_user = requests.get(f"{BASE_URL}/api/users/12")
        logger.info(f"GET /api/users/12 - Status: {response_last_user.status_code}")

        assert response_last_user.status_code == 200
        user12: SingleUserResponse = SingleUserResponse(**response_last_user.json())

        assert user12.data.first_name == "Rachel"
        assert user12.data.last_name == "Howell"
        logger.info("Different users work, schemas valid")

    def test_middle_user(self) -> None:
        """Тест пользователя из середины списка"""
        response = requests.get(f"{BASE_URL}/api/users/7")
        logger.info(f"GET /api/users/7 - Status: {response.status_code}")

        assert response.status_code == 200
        user: SingleUserResponse = SingleUserResponse(**response.json())

        assert user.data.first_name == "Michael"
        assert user.data.last_name == "Lawson"
        logger.info("User 7 found, schema valid")


class TestResources:
    """Тесты для ресурсов"""

    def test_list_resources(self) -> None:
        """Тест списка ресурсов"""
        # GET /api/unknown
        pass

    def test_single_resource(self) -> None:
        """Тест получения одного ресурса"""
        # GET /api/unknown/2
        pass

    def test_single_resource_not_found(self) -> None:
        """Тест получения несуществующего ресурса"""
        # GET /api/unknown/23
        pass


class TestCRUD:
    """Тесты для создания, обновления, удаления"""

    def test_create_user(self) -> None:
        """Тест создания пользователя"""
        # POST /api/users
        pass

    def test_update_user_put(self) -> None:
        """Тест полного обновления пользователя"""
        # PUT /api/users/2
        pass

    def test_update_user_patch(self) -> None:
        """Тест частичного обновления пользователя"""
        # PATCH /api/users/2
        pass

    def test_delete_user(self) -> None:
        """Тест удаления пользователя"""
        # DELETE /api/users/2
        pass


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
        # POST /api/login (неверные данные)
        pass


class TestSpecial:
    """Специальные тесты"""

    def test_delayed_response(self) -> None:
        """Тест задержанного ответа"""
        # GET /api/users?delay=3
        pass
