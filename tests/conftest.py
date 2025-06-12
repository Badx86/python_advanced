import dotenv
import pytest
import requests
import os
from typing import Dict, Optional, Any


class APIClient:
    """API клиент для всех HTTP методов"""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """GET запрос"""
        return requests.get(
            f"{self.base_url}{endpoint}", params=params, headers=headers
        )

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """POST запрос"""
        return requests.post(
            f"{self.base_url}{endpoint}", json=json, data=data, headers=headers
        )

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """PUT запрос"""
        return requests.put(
            f"{self.base_url}{endpoint}", json=json, data=data, headers=headers
        )

    def patch(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """PATCH запрос"""
        return requests.patch(
            f"{self.base_url}{endpoint}", json=json, data=data, headers=headers
        )

    def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """DELETE запрос"""
        return requests.delete(f"{self.base_url}{endpoint}", headers=headers)


@pytest.fixture(autouse=True)
def envs():
    dotenv.load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    """Базовый URL для API"""
    return os.getenv("API_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def health_check(base_url: str) -> None:
    """Проверяет доступность сервиса перед запуском всех тестов"""
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code != 200:
            pytest.exit(f"Service unhealthy: {response.status_code}")
    except requests.exceptions.RequestException as e:
        pytest.exit(f"Service unavailable: {e}")


@pytest.fixture
def api_client(base_url: str, health_check) -> APIClient:
    """API клиент для всех HTTP методов"""
    return APIClient(base_url)
