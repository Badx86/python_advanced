import requests
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


class TestAPI:
    """Тесты для API"""

    def test_list_users_page_1(self):
        """Тест первой страницы"""
        response = requests.get(f"{BASE_URL}/api/users?page=1")
        logger.info(f"GET /api/users?page=1 - Status: {response.status_code}")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 6
        assert data["total"] == 12
        assert data["total_pages"] == 2
        assert len(data["data"]) == 6
        logger.info("Page 1 works")

    def test_list_users_page_2(self):
        """Тест второй страницы"""
        response = requests.get(f"{BASE_URL}/api/users?page=2")
        logger.info(f"GET /api/users?page=2 - Status: {response.status_code}")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["per_page"] == 6
        assert len(data["data"]) == 6
        assert data["data"][0]["id"] == 7
        logger.info("Page 2 works")

    def test_default_params(self):
        """Тест без параметров"""
        response = requests.get(f"{BASE_URL}/api/users")
        logger.info(f"GET /api/users (default) - Status: {response.status_code}")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 6
        logger.info("Default params work")

    def test_single_user_exists(self):
        """Тест получения существующего пользователя"""
        response = requests.get(f"{BASE_URL}/api/users/2")
        logger.info(f"GET /api/users/2 - Status: {response.status_code}")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == 2
        assert data["data"]["email"] == "janet.weaver@reqres.in"
        assert data["data"]["first_name"] == "Janet"
        assert data["data"]["last_name"] == "Weaver"
        logger.info("User 2 found")

    def test_single_user_not_found(self):
        """Тест получения несуществующего пользователя"""
        response = requests.get(f"{BASE_URL}/api/users/999")
        logger.info(f"GET /api/users/999 - Status: {response.status_code}")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == {}
        logger.info("User 999 not found (404)")

    def test_different_users(self):
        """Тест получения разных пользователей"""
        # Первый пользователь
        response1 = requests.get(f"{BASE_URL}/api/users/1")
        logger.info(f"GET /api/users/1 - Status: {response1.status_code}")

        assert response1.status_code == 200
        user1 = response1.json()["data"]
        assert user1["first_name"] == "George"
        assert user1["last_name"] == "Bluth"

        # Последний пользователь
        response12 = requests.get(f"{BASE_URL}/api/users/12")
        logger.info(f"GET /api/users/12 - Status: {response12.status_code}")

        assert response12.status_code == 200
        user12 = response12.json()["data"]
        assert user12["first_name"] == "Rachel"
        assert user12["last_name"] == "Howell"
        logger.info("Different users work")

    def test_middle_user(self):
        """Тест пользователя из середины списка"""
        response = requests.get(f"{BASE_URL}/api/users/7")
        logger.info(f"GET /api/users/7 - Status: {response.status_code}")

        assert response.status_code == 200
        user = response.json()["data"]
        assert user["first_name"] == "Michael"
        assert user["last_name"] == "Lawson"
        logger.info("User 7 found")
