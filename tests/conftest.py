import allure
import dotenv
import pytest
import requests
import os
import sys
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


# ========================================
# Allure Reporting Configuration
# ========================================


@pytest.fixture(scope="session", autouse=True)
def allure_environment(base_url: str):
    """Добавляет информацию об окружении в Allure отчет"""
    # Создаем environment.properties для Allure
    environment_properties = [
        f"API_URL={base_url}",
        f"Python_Version={sys.version.split()[0]}",
        f"Database_Engine={os.getenv('DATABASE_ENGINE', 'Not specified')}",
        f"Host={os.getenv('HOST', 'localhost')}",
        f"Port={os.getenv('PORT', '8000')}",
        f"App_Version={os.getenv('APP_VERSION', '1.0.0')}",
    ]

    # Записываем в файл для Allure
    allure_results_dir = "allure-results"
    if not os.path.exists(allure_results_dir):
        os.makedirs(allure_results_dir)

    with open(f"{allure_results_dir}/environment.properties", "w") as f:
        for prop in environment_properties:
            f.write(f"{prop}\n")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Добавляет дополнительную информацию при падении тестов"""
    outcome = yield
    report = outcome.get_result()

    # Добавляем информацию только при падении тестов
    if report.when == "call" and report.failed:
        # Получаем информацию о тесте
        test_name = item.name
        test_file = item.fspath.basename

        # Добавляем attachment с информацией об ошибке
        if hasattr(report, "longrepr") and report.longrepr:
            allure.attach(
                str(report.longrepr),
                name=f"Test Failure Details: {test_name}",
                attachment_type=allure.attachment_type.TEXT,
            )

        # Добавляем информацию о тесте
        allure.attach(
            f"Test: {test_name}\nFile: {test_file}\nDuration: {report.duration:.2f}s",
            name="Test Information",
            attachment_type=allure.attachment_type.TEXT,
        )


def pytest_configure(config):
    """Конфигурация Allure categories"""
    # Возможность добавления кастомных категорий
    if hasattr(config, "_allure_config"):
        # Создаем categories.json для группировки ошибок
        categories = [
            {
                "name": "API Response Errors",
                "messageRegex": ".*status_code.*|.*HTTP.*|.*Response.*",
                "traceRegex": ".*requests.*|.*urllib.*",
            },
            {
                "name": "Database Errors",
                "messageRegex": ".*database.*|.*SQL.*|.*connection.*",
                "traceRegex": ".*sqlalchemy.*|.*psycopg.*",
            },
            {
                "name": "Validation Errors",
                "messageRegex": ".*validation.*|.*assert.*|.*ValidationError.*",
                "traceRegex": ".*pydantic.*|.*marshmallow.*",
            },
            {
                "name": "Service Unavailable",
                "messageRegex": ".*Service unavailable.*|.*Connection.*|.*timeout.*",
                "traceRegex": ".*requests.*",
            },
        ]

        allure_results_dir = "allure-results"
        if not os.path.exists(allure_results_dir):
            os.makedirs(allure_results_dir)

        import json

        with open(f"{allure_results_dir}/categories.json", "w") as f:
            json.dump(categories, f, indent=2)
