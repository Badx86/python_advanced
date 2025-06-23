"""
Конфигурация pytest с управлением окружением,
интеграцией API клиента и комплексными фикстурами тестовых данных
"""

import allure
import dotenv
import pytest
import requests
import os
import sys
from typing import Dict, Optional, Any, Generator
from mimesis import Person, Text, Numeric

from tests.api_client import ReqresAPIClient, Environment, TestDataManager


# ===================================
# КОНФИГУРАЦИЯ PYTEST
# ===================================


def pytest_addoption(parser):
    """Добавляет опции командной строки"""
    parser.addoption(
        "--env",
        action="store",
        default="local",
        help="Environment: local, staging, prod, docker",
    )
    parser.addoption(
        "--skip-cleanup", action="store_true", help="Skip automatic test data cleanup"
    )


@pytest.fixture(autouse=True)
def load_env():
    """Автоматически загружает переменные окружения"""
    dotenv.load_dotenv()


# ===================================
# ФИКСТУРЫ ОКРУЖЕНИЯ И КЛИЕНТА
# ===================================


@pytest.fixture(scope="session")
def environment(request) -> Environment:
    """Конфигурация тестового окружения"""
    env_name = request.config.getoption("--env")
    return Environment.from_env_name(env_name)


@pytest.fixture(scope="session")
def health_check(environment: Environment) -> None:
    """Проверяет доступность сервиса перед выполнением тестов"""
    try:
        response = requests.get(f"{environment.base_url}/status", timeout=5)
        if response.status_code != 200:
            pytest.exit(
                f"Service unhealthy on {environment.base_url}: {response.status_code}"
            )

        allure.attach(
            f"Environment: {environment.base_url}\nStatus: Healthy",
            "Pre-test Health Check",
            allure.attachment_type.TEXT,
        )

    except requests.exceptions.RequestException as e:
        pytest.exit(f"Service unavailable on {environment.base_url}: {e}")


@pytest.fixture
def api(environment: Environment, health_check) -> ReqresAPIClient:
    """Основной экземпляр API клиента"""
    return ReqresAPIClient(environment)


@pytest.fixture
def test_data(api: ReqresAPIClient, request) -> Generator[TestDataManager, None, None]:
    """Менеджер тестовых данных с автоматической очисткой"""
    manager = TestDataManager(api)
    yield manager

    # Очистка, если явно не пропущена
    if not request.config.getoption("--skip-cleanup"):
        manager.cleanup_all()


# ===================================
# ФИКСТУРЫ СОВМЕСТИМОСТИ
# ===================================


@pytest.fixture(scope="session")
def base_url(environment: Environment) -> str:
    """Совместимость - базовый URL"""
    return environment.base_url


@pytest.fixture
def api_client(environment: Environment, health_check):
    """Legacy API клиент для обратной совместимости"""

    return APIClient(environment.base_url)


@pytest.fixture
def reqres_api(api: ReqresAPIClient) -> ReqresAPIClient:
    """Алиас для основного API клиента"""
    return api


# ===================================
# ГЕНЕРАТОРЫ ТЕСТОВЫХ ДАННЫХ
# ===================================


@pytest.fixture
def fake() -> Dict[str, Any]:
    """Генераторы фейковых данных"""
    return {"person": Person(), "text": Text(), "numeric": Numeric()}


@pytest.fixture
def user_data(fake) -> Dict[str, str]:
    """Генерирует реалистичные данные пользователя"""
    return {"name": fake["person"].full_name(), "job": fake["person"].occupation()}


@pytest.fixture
def resource_data(fake) -> Dict[str, Any]:
    """Генерирует реалистичные данные ресурса"""
    return {
        "name": fake["text"].color().lower(),
        "year": fake["numeric"].integer_number(2020, 2030),
        "color": fake["text"].hex_color(),
        "pantone_value": f"{fake['text'].word().upper()}-{fake['numeric'].integer_number(100, 999)}",
    }


@pytest.fixture
def auth_data() -> Dict[str, str]:
    """Валидные данные для аутентификации"""
    return {"email": "user@gmail.com", "password": "securepass123"}


# ===================================
# СПЕЦИФИЧНЫЕ ФИКСТУРЫ ТЕСТОВЫХ ДАННЫХ
# ===================================


@pytest.fixture
def test_user_data() -> Dict[str, str]:
    """Статичные тестовые данные пользователя для предсказуемых тестов"""
    return {"name": "Test User", "job": "QA Engineer"}


@pytest.fixture
def test_resource_data() -> Dict[str, Any]:
    """Статичные тестовые данные ресурса"""
    return {
        "name": "test color",
        "year": 2024,
        "color": "#FF5733",
        "pantone_value": "TEST-123",
    }


@pytest.fixture
def valid_auth_data() -> Dict[str, str]:
    """Валидные данные аутентификации для тестов"""
    return {"email": "test@example.com", "password": "securepass123"}


# ===================================
# ПАРАМЕТРИЗОВАННЫЕ ТЕСТОВЫЕ ДАННЫЕ
# ===================================


@pytest.fixture(
    params=[{"page": 1, "size": 6}, {"page": 2, "size": 6}, {"page": 1, "size": 12}]
)
def pagination_params(request) -> Dict[str, int]:
    """Параметризованные данные пагинации"""
    return request.param


@pytest.fixture(
    params=[
        ("John Doe", "Developer"),
        ("Jane Smith", "Designer"),
        ("Bob Wilson", "Manager"),
    ]
)
def user_test_cases(request) -> tuple:
    """Параметризованные тестовые случаи пользователей"""
    return request.param


# ===================================
# КОНФИГУРАЦИЯ ALLURE ОТЧЕТНОСТИ
# ===================================


@pytest.fixture(scope="session", autouse=True)
def allure_environment(environment: Environment):
    """Настраивает свойства окружения для Allure"""

    db_engine = os.getenv("DATABASE_ENGINE", "Not specified")
    if db_engine != "Not specified":
        # Скрываем пароль: postgres:example@ -> postgres:***@
        import re

        db_engine_masked = re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", db_engine)
    else:
        db_engine_masked = db_engine

    properties = [
        f"Environment={environment.base_url}",
        f"Timeout={environment.timeout}s",
        f"Python_Version={sys.version.split()[0]}",
        f"Database_Engine={db_engine_masked}",
        f"App_Version={os.getenv('APP_VERSION', '1.1.0')}",
        f"Host={os.getenv('HOST', 'localhost')}",
        f"Port={os.getenv('PORT', '8000')}",
        f"Test_Framework=pytest + voluptuous + fluent API",
    ]

    # Создаем файл окружения для allure
    allure_dir = "allure-results"
    os.makedirs(allure_dir, exist_ok=True)

    with open(f"{allure_dir}/environment.properties", "w") as f:
        for prop in properties:
            f.write(f"{prop}\n")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Улучшенная отчетность тестов с деталями ошибок"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Извлекаем информацию о тесте
        test_name = item.name
        test_file = item.fspath.basename

        # Добавляем детали ошибки в Allure
        if hasattr(report, "longrepr") and report.longrepr:
            allure.attach(
                str(report.longrepr),
                f"Test Failure: {test_name}",
                allure.attachment_type.TEXT,
            )

        # Добавляем метаданные теста
        allure.attach(
            f"Test: {test_name}\n"
            f"File: {test_file}\n"
            f"Duration: {report.duration:.2f}s\n"
            f"Stage: {report.when}",
            "Test Metadata",
            allure.attachment_type.TEXT,
        )


def pytest_configure(config):
    """Настраивает категории Allure и маркеры"""
    import json

    # Категории ошибок для Allure
    categories = [
        {
            "name": "API Schema Validation",
            "messageRegex": ".*Schema validation failed.*|.*voluptuous.*",
            "traceRegex": ".*pytest_voluptuous.*",
        },
        {
            "name": "HTTP Response Errors",
            "messageRegex": ".*status_code.*|.*HTTP.*|.*Response.*",
            "traceRegex": ".*requests.*",
        },
        {
            "name": "Database Issues",
            "messageRegex": ".*database.*|.*SQL.*|.*connection.*",
            "traceRegex": ".*sqlalchemy.*",
        },
        {
            "name": "Environment Issues",
            "messageRegex": ".*Service unavailable.*|.*timeout.*",
            "traceRegex": ".*requests.*",
        },
    ]

    allure_dir = "allure-results"
    os.makedirs(allure_dir, exist_ok=True)

    with open(f"{allure_dir}/categories.json", "w") as f:
        json.dump(categories, f, indent=2)

    # Регистрируем кастомные маркеры
    config.addinivalue_line("markers", "smoke: Smoke тесты базовой функциональности")
    config.addinivalue_line("markers", "auth: Тесты аутентификации")
    config.addinivalue_line("markers", "crud: Тесты CRUD операций")
    config.addinivalue_line("markers", "pagination: Тесты пагинации")
    config.addinivalue_line("markers", "schema: Тесты валидации схем")
    config.addinivalue_line("markers", "slow: Медленные тесты")


# ===================================
# ОБРАТНАЯ СОВМЕСТИМОСТЬ
# ===================================


class APIClient:
    """Legacy API клиент для обратной совместимости"""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
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
        return requests.patch(
            f"{self.base_url}{endpoint}", json=json, data=data, headers=headers
        )

    def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        return requests.delete(f"{self.base_url}{endpoint}", headers=headers)
