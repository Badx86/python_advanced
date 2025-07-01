"""
API клиент с интеграцией валидации схем
"""

from typing import Dict, Any, Union
import requests
from dataclasses import dataclass
import logging
import os
import allure
from http import HTTPStatus

from tests.schemas import schemas

logger = logging.getLogger(__name__)


@dataclass
class Environment:
    """Конфигурация тестового окружения"""

    base_url: str
    timeout: int = 30

    @classmethod
    def from_env_name(cls, env_name: str) -> "Environment":
        """Фабричный метод для создания окружения"""
        env_configs = {
            "local": cls("http://localhost:8000"),
            "staging": cls("https://staging-api.example.com"),
            "prod": cls("https://api.example.com"),
            "docker": cls("http://localhost:8000"),
        }

        # Поддержка кастомного URL через переменную окружения
        if custom_url := os.getenv("API_URL"):
            return cls(custom_url)

        return env_configs.get(env_name, env_configs["local"])


class APIResponse:
    """Расширенная обертка ответа с валидацией схем"""

    def __init__(self, response: requests.Response):
        self.response = response
        self._json_data = None

    @property
    def status_code(self) -> int:
        return self.response.status_code

    @property
    def json_data(self) -> Dict[str, Any]:
        """Кешированные JSON данные"""
        if self._json_data is None:
            self._json_data = self.response.json()
        return self._json_data

    def validate_schema(self, schema_name: str) -> "APIResponse":
        """Валидирует ответ в соответствии со схемой и возвращает self для цепочки вызовов"""
        with allure.step(f"Validate response schema: {schema_name}"):
            try:
                schemas.validate(schema_name, self.json_data)
                logger.debug(f"Schema validation passed: {schema_name}")
            except Exception as e:
                allure.attach(
                    str(self.json_data),
                    "Failed Response Data",
                    allure.attachment_type.JSON,
                )
                raise AssertionError(
                    f"Schema '{schema_name}' validation failed: {e}"
                )
        return self

    # ===================================
    # CONVENIENCE МЕТОДЫ ДЛЯ ВАЛИДАЦИИ
    # ===================================

    def validate_users_list(self) -> "APIResponse":
        """Валидирует ответ списка пользователей"""
        return self.validate_schema("USERS_LIST")

    def validate_single_user(self) -> "APIResponse":
        """Валидирует ответ одного пользователя"""
        return self.validate_schema("SINGLE_USER")

    def validate_user_created(self) -> "APIResponse":
        """Валидирует ответ создания пользователя"""
        return self.validate_schema("USER_CREATED")

    def validate_user_updated(self) -> "APIResponse":
        """Валидирует ответ обновления пользователя"""
        return self.validate_schema("USER_UPDATED")

    def validate_resources_list(self) -> "APIResponse":
        """Валидирует ответ списка ресурсов"""
        return self.validate_schema("RESOURCES_LIST")

    def validate_single_resource(self) -> "APIResponse":
        """Валидирует ответ одного ресурса"""
        return self.validate_schema("SINGLE_RESOURCE")

    def validate_resource_created(self) -> "APIResponse":
        """Валидирует ответ создания ресурса"""
        return self.validate_schema("RESOURCE_CREATED")

    def validate_resource_updated(self) -> "APIResponse":
        """Валидирует ответ обновления ресурса"""
        return self.validate_schema("RESOURCE_UPDATED")

    def validate_register_success(self) -> "APIResponse":
        """Валидирует ответ успешной регистрации"""
        return self.validate_schema("REGISTER_SUCCESS")

    def validate_login_success(self) -> "APIResponse":
        """Валидирует ответ успешного логина"""
        return self.validate_schema("LOGIN_SUCCESS")

    def validate_system_health(self) -> "APIResponse":
        """Валидирует ответ проверки здоровья системы"""
        return self.validate_schema("HEALTH_STATUS")

    def validate_api_error(self) -> "APIResponse":
        """Валидирует ответ с ошибкой API"""
        return self.validate_schema("API_ERROR")

    def assert_status(self, expected: HTTPStatus) -> "APIResponse":
        """Проверяет HTTP статус и возвращает self для цепочки вызовов"""
        with allure.step(f"Assert HTTP status: {expected.value}"):
            assert (
                self.status_code == expected.value
            ), f"Expected {expected.value}, got {self.status_code}"
        return self

    def extract(self, *keys) -> Union[Any, tuple]:
        """Извлекает значения из JSON ответа"""
        if len(keys) == 1:
            return self.json_data.get(keys[0])
        return tuple(self.json_data.get(key) for key in keys)


class ReqresAPIClient:
    """
    API клиент с валидацией схем

    - Fluent интерфейс с цепочкой методов
    - Явная валидация схем
    - Настройка в зависимости от окружения
    """

    def __init__(self, environment: Environment):

        self.env = environment
        self.session = requests.Session()
        self.session.timeout = environment.timeout
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

        logger.info(f"API Client initialized: {environment.base_url}")

    def request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """Внутренний метод запроса с логированием"""
        url = f"{self.env.base_url}{endpoint}"

        with allure.step(f"{method.upper()} {endpoint}"):
            logger.debug(f"{method.upper()} {url} | {kwargs}")

            response = self.session.request(method, url, **kwargs)

            # Автоматически прикрепляем ответ для отладки
            if response.text:
                allure.attach(
                    response.text,
                    f"Response Body ({response.status_code})",
                    allure.attachment_type.JSON,
                )

            return APIResponse(response)

    # ===================================
    # USERS API - Fluent интерфейс
    # ===================================

    def users(self) -> "UsersAPI":
        """Доступ к эндпоинтам Users API"""
        return UsersAPI(self)

    def resources(self) -> "ResourcesAPI":
        """Доступ к эндпоинтам Resources API"""
        return ResourcesAPI(self)

    def auth(self) -> "AuthAPI":
        """Доступ к эндпоинтам Authentication API"""
        return AuthAPI(self)

    def system(self) -> "SystemAPI":
        """Доступ к эндпоинтам System API"""
        return SystemAPI(self)


class UsersAPI:
    """Эндпоинты Users API без автоматической валидации схем"""

    def __init__(self, client: ReqresAPIClient):
        self.client = client

    def list(self, page: int = 1, size: int = 6, delay: int = 0) -> APIResponse:
        """Получить список пользователей"""
        params = {"page": page, "size": size}

        if delay > 0:
            params["delay"] = delay

        return self.client.request("GET", "/api/users", params=params).assert_status(
            HTTPStatus.OK
        )

    def get(self, user_id: int) -> APIResponse:
        """Получить одного пользователя"""
        return self.client.request("GET", f"/api/users/{user_id}").assert_status(
            HTTPStatus.OK
        )

    def get_raw(self, user_id: int) -> APIResponse:
        """Получить одного пользователя без автоматической проверки статуса (для edge cases)"""
        return self.client.request("GET", f"/api/users/{user_id}")

    def create(self, name: str, job: str) -> APIResponse:
        """Создать пользователя"""
        data = {"name": name, "job": job}
        return self.client.request("POST", "/api/users", json=data).assert_status(
            HTTPStatus.CREATED
        )

    def update(
        self, user_id: int, name: str, job: str, method: str = "PUT"
    ) -> APIResponse:
        """Обновить пользователя"""
        data = {"name": name, "job": job}
        http_method = "PUT" if method == "PUT" else "PATCH"
        return self.client.request(
            http_method, f"/api/users/{user_id}", json=data
        ).assert_status(HTTPStatus.OK)

    def delete(self, user_id: int) -> APIResponse:
        """Удалить пользователя"""
        return self.client.request("DELETE", f"/api/users/{user_id}").assert_status(
            HTTPStatus.NO_CONTENT
        )

    def get_404(self, user_id: int) -> APIResponse:
        """Получить несуществующего пользователя (ожидается 404)"""
        return self.client.request("GET", f"/api/users/{user_id}").assert_status(
            HTTPStatus.NOT_FOUND
        )


class ResourcesAPI:
    """Эндпоинты Resources API без автоматической валидации схем"""

    def __init__(self, client: ReqresAPIClient):
        self.client = client

    def list(self, page: int = 1, size: int = 6) -> APIResponse:
        """Получить список ресурсов"""
        params = {"page": page, "size": size}
        return self.client.request(
            "GET", "/api/resources", params=params
        ).assert_status(HTTPStatus.OK)

    def get(self, resource_id: int) -> APIResponse:
        """Получить один ресурс"""
        return self.client.request(
            "GET", f"/api/resources/{resource_id}"
        ).assert_status(HTTPStatus.OK)

    def get_raw(self, resource_id: int) -> APIResponse:
        """Получить один ресурс без автоматической проверки статуса (для edge cases)"""
        return self.client.request("GET", f"/api/resources/{resource_id}")

    def create(
        self, name: str, year: int, color: str, pantone_value: str
    ) -> APIResponse:
        """Создать ресурс"""
        data = {
            "name": name,
            "year": year,
            "color": color,
            "pantone_value": pantone_value,
        }
        return self.client.request("POST", "/api/resources", json=data).assert_status(
            HTTPStatus.CREATED
        )

    def update(
        self, resource_id: int, data: Dict[str, Any], method: str = "PUT"
    ) -> APIResponse:
        """Обновить ресурс"""
        http_method = "PUT" if method == "PUT" else "PATCH"
        return self.client.request(
            http_method, f"/api/resources/{resource_id}", json=data
        ).assert_status(HTTPStatus.OK)

    def delete(self, resource_id: int) -> APIResponse:
        """Удалить ресурс"""
        return self.client.request(
            "DELETE", f"/api/resources/{resource_id}"
        ).assert_status(HTTPStatus.NO_CONTENT)


class AuthAPI:
    """Эндпоинты Authentication API без автоматической валидации схем"""

    def __init__(self, client: ReqresAPIClient):
        self.client = client

    def register(self, email: str, password: str) -> APIResponse:
        """Регистрировать пользователя"""
        data = {"email": email, "password": password}
        return self.client.request("POST", "/api/register", json=data).assert_status(
            HTTPStatus.CREATED
        )

    def login(self, email: str, password: str) -> APIResponse:
        """Войти в систему"""
        data = {"email": email, "password": password}
        return self.client.request("POST", "/api/login", json=data).assert_status(
            HTTPStatus.OK
        )


class SystemAPI:
    """Эндпоинты System API без автоматической валидации схем"""

    def __init__(self, client: ReqresAPIClient):
        self.client = client

    def status(self) -> APIResponse:
        """Получить статус системы"""
        return self.client.request("GET", "/status").assert_status(HTTPStatus.OK)


# ===================================
# FLUENT ХЕЛПЕРЫ И УТИЛИТЫ
# ===================================


class TestDataManager:
    """Управляет жизненным циклом тестовых данных с автоматической очисткой"""

    def __init__(self, api_client: ReqresAPIClient):

        self.api = api_client
        self.created_users = []
        self.created_resources = []

    def create_user(self, name: str, job: str) -> int:
        """Создать пользователя и отследить для очистки"""
        response = self.api.users().create(name, job).validate_user_created()
        user_id = int(response.extract("id"))

        self.created_users.append(user_id)
        return user_id

    def create_resource(
        self, name: str, year: int, color: str, pantone_value: str
    ) -> int:
        """Создать ресурс и отследить для очистки"""
        response = (
            self.api.resources()
            .create(name, year, color, pantone_value)
            .validate_resource_created()
        )
        resource_id = int(response.extract("id"))

        self.created_resources.append(resource_id)
        return resource_id

    def cleanup_all(self):
        """Очистить все созданные тестовые данные"""
        for user_id in self.created_users:

            try:
                self.api.users().delete(user_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup user {user_id}: {e}")

        for resource_id in self.created_resources:

            try:
                self.api.resources().delete(resource_id)
            except Exception as e:
                logger.warning(f"Failed to cleanup resource {resource_id}: {e}")

        self.created_users.clear()
        self.created_resources.clear()
        logger.info("Test data cleanup completed")
