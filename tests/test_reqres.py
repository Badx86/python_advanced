import requests
import logging
from tests.assertions import (
    assert_users_list_response,
    assert_user_response,
    assert_resources_list_response,
    assert_resource_response,
    assert_404_error,
    assert_user_fields,
    assert_resource_fields,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


class TestUsers:
    """Тесты для пользователей"""

    def test_list_users_page_1(self, api_client) -> None:
        """Тест первой страницы"""
        response = api_client.get("/api/users", params={"page": 1})
        users_response = assert_users_list_response(response, "/api/users?page=1")

        assert len(users_response.data) == 6
        logger.info("Page 1 works, schema valid")

    def test_list_users_page_2(self) -> None:
        """Тест второй страницы"""
        response = requests.get(f"{BASE_URL}/api/users?page=2")
        users_response = assert_users_list_response(
            response, "/api/users?page=2", page=2
        )

        assert users_response.data[0].id == 7
        logger.info("Page 2 works, schema valid")

    def test_default_params(self, api_client) -> None:
        """Тест без параметров"""
        response = api_client.get("/api/users")
        assert_users_list_response(response, "/api/users (default)")
        logger.info("Default params work, schema valid")

    def test_single_user_exists(self, api_client) -> None:
        """Тест получения существующего пользователя"""
        response = api_client.get("/api/users/2")
        user_response = assert_user_response(response, "/api/users/2")

        assert_user_fields(
            user_response.data.dict(),
            expected_id=2,
            expected_email="janet.weaver@reqres.in",
            expected_first_name="Janet",
            expected_last_name="Weaver",
        )
        logger.info("User 2 found, schema valid")

    def test_single_user_not_found(self) -> None:
        """Тест получения несуществующего пользователя"""
        response = requests.get(f"{BASE_URL}/api/users/999")
        assert_404_error(response, "/api/users/999")
        logger.info("User 999 not found (404)")

    def test_single_user_23_not_found(self) -> None:
        """Тест получения пользователя 23 (как в оригинальном reqres)"""
        response = requests.get(f"{BASE_URL}/api/users/23")
        assert_404_error(response, "/api/users/23")
        logger.info("User 23 not found (404)")

    def test_different_users(self) -> None:
        """Тест получения разных пользователей"""
        # Первый пользователь
        response_first = requests.get(f"{BASE_URL}/api/users/1")
        user1 = assert_user_response(response_first, "/api/users/1")
        assert_user_fields(
            user1.data.dict(), 1, "george.bluth@reqres.in", "George", "Bluth"
        )

        # Последний пользователь
        response_last = requests.get(f"{BASE_URL}/api/users/12")
        user12 = assert_user_response(response_last, "/api/users/12")
        assert_user_fields(
            user12.data.dict(), 12, "rachel.howell@reqres.in", "Rachel", "Howell"
        )

        logger.info("Different users work, schemas valid")

    def test_middle_user(self) -> None:
        """Тест пользователя из середины списка"""
        response = requests.get(f"{BASE_URL}/api/users/7")
        user = assert_user_response(response, "/api/users/7")
        assert_user_fields(
            user.data.dict(), 7, "michael.lawson@reqres.in", "Michael", "Lawson"
        )
        logger.info("User 7 found, schema valid")


class TestResources:
    """Тесты для ресурсов"""

    def test_list_resources(self, api_client) -> None:
        """Тест списка ресурсов"""
        response = api_client.get("/api/unknown")
        resources_response = assert_resources_list_response(response, "/api/unknown")

        assert resources_response.data[0].name == "cerulean"
        assert resources_response.data[0].year == 2000
        logger.info("Resources list works, schema valid")

    def test_single_resource(self, api_client) -> None:
        """Тест получения одного ресурса"""
        response = api_client.get("/api/unknown/2")
        resource_response = assert_resource_response(response, "/api/unknown/2")

        assert_resource_fields(
            resource_response.data.dict(),
            expected_id=2,
            expected_name="fuchsia rose",
            expected_year=2001,
            expected_color="#C74375",
            expected_pantone="17-2031",
        )
        logger.info("Resource 2 found, schema valid")

    def test_single_resource_not_found(self) -> None:
        """Тест получения несуществующего ресурса"""
        response = requests.get(f"{BASE_URL}/api/unknown/23")
        assert_404_error(response, "/api/unknown/23")
        logger.info("Resource 23 not found (404)")

    def test_resources_page_2(self) -> None:
        """Тест второй страницы ресурсов"""
        response = requests.get(f"{BASE_URL}/api/unknown?page=2")
        resources_response = assert_resources_list_response(
            response, "/api/unknown?page=2", page=2
        )

        assert resources_response.data[0].id == 7
        assert resources_response.data[0].name == "sand dollar"
        logger.info("Page 2 resources work, schema valid")

    def test_resources_default_params(self, api_client) -> None:
        """Тест ресурсов без параметров"""
        response = api_client.get("/api/unknown")
        assert_resources_list_response(response, "/api/unknown (default)")
        logger.info("Default params for resources work, schema valid")

    def test_first_and_last_resource(self) -> None:
        """Тест первого и последнего ресурса"""
        # Первый ресурс
        response_first = requests.get(f"{BASE_URL}/api/unknown/1")
        resource1 = assert_resource_response(response_first, "/api/unknown/1")
        assert_resource_fields(
            resource1.data.dict(), 1, "cerulean", 2000, "#98B2D1", "15-4020"
        )

        # Последний ресурс
        response_last = requests.get(f"{BASE_URL}/api/unknown/12")
        resource12 = assert_resource_response(response_last, "/api/unknown/12")
        assert_resource_fields(
            resource12.data.dict(), 12, "honeysuckle", 2011, "#D94F70", "18-2120"
        )

        logger.info("First and last resources work, schemas valid")


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
