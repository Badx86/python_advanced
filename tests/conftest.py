import pytest
import requests
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


@pytest.fixture
def base_url() -> str:
    """Базовый URL для API"""
    return "http://localhost:8000"


@pytest.fixture
def api_client(base_url: str) -> APIClient:
    """API клиент для всех HTTP методов"""
    return APIClient(base_url)


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Заголовки с API ключом для аутентификации"""
    return {"x-api-key": "reqres-free-v1"}


@pytest.fixture
def sample_user_data() -> Dict[str, str]:
    """Тестовые данные пользователя"""
    return {"name": "morpheus", "job": "leader"}
