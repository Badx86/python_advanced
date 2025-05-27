import pytest
import requests


@pytest.fixture
def base_url():
    """Базовый URL для API"""
    return "http://localhost:8000"


@pytest.fixture
def api_client(base_url):
    """API клиент для всех HTTP методов"""

    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url

        def get(self, endpoint, params=None, headers=None):
            """GET"""
            return requests.get(
                f"{self.base_url}{endpoint}", params=params, headers=headers
            )

        def post(self, endpoint, json=None, data=None, headers=None):
            """POST"""
            return requests.post(
                f"{self.base_url}{endpoint}", json=json, data=data, headers=headers
            )

        def put(self, endpoint, json=None, data=None, headers=None):
            """PUT"""
            return requests.put(
                f"{self.base_url}{endpoint}", json=json, data=data, headers=headers
            )

        def patch(self, endpoint, json=None, data=None, headers=None):
            """PATCH"""
            return requests.patch(
                f"{self.base_url}{endpoint}", json=json, data=data, headers=headers
            )

        def delete(self, endpoint, headers=None):
            """DELETE"""
            return requests.delete(f"{self.base_url}{endpoint}", headers=headers)

    return APIClient(base_url)


@pytest.fixture
def auth_headers():
    """Заголовки с API ключом для аутентификации"""
    return {"x-api-key": "reqres-free-v1"}


@pytest.fixture
def sample_user_data():
    """Тестовые данные пользователя"""
    return {"name": "morpheus", "job": "leader"}
