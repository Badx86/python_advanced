import allure
import pytest
import logging

logger = logging.getLogger(__name__)


@allure.feature("Demo Test Statuses")
class TestDemoStatuses:
    """Демонстрация различных статусов тестов для Allure отчета"""

    @allure.title("Test that should pass")
    def test_pass_example(self, api_client) -> None:
        """Обычный проходящий тест"""
        response = api_client.get("/status")
        assert response.status_code == 200
        logger.info("✅ This test passed as expected")

    @allure.title("Test that should be skipped")
    @pytest.mark.skip(reason="Демонстрация skip статуса для Allure отчета")
    def test_skip_example(self, api_client) -> None:
        """Пропущенный тест"""
        # Этот код не выполнится
        assert False, "This should not run"

    @allure.title("Test expected to fail but might pass")
    @pytest.mark.xfail(reason="Демонстрация xfail статуса - ожидаем падение")
    def test_xfail_example(self, api_client) -> None:
        """Тест который должен упасть, но может пройти"""
        # Намеренно делаем тест который может как пройти, так и упасть
        response = api_client.get("/status")
        # Проверяем что статус НЕ health
        data = response.json()
        assert data["status"] != "healthy", "Expected status to NOT be healthy"

    @allure.title("Test that will definitely fail")
    def test_fail_example(self, api_client) -> None:
        """Тест который обязательно упадет"""
        response = api_client.get("/status")

        # Намеренно неправильная проверка чтобы тест упал
        assert (
            response.status_code == 500
        ), "Deliberately failing test for demo purposes"
