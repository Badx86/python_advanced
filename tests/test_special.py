import logging
import time
import pytest
from tests.assertions import api

logger = logging.getLogger(__name__)


class TestSpecial:
    """Специальные тесты"""

    @pytest.mark.parametrize("delay_seconds", [1, 2])
    def test_delayed_response(self, api_client, delay_seconds) -> None:
        """Тест задержанного ответа"""
        start_time = time.time()

        response = api_client.get("/api/users", params={"delay": delay_seconds})
        actual_duration = time.time() - start_time

        api.check_delayed_response(
            response, f"/api/users?delay={delay_seconds}", delay_seconds
        )

        logger.info(
            f"Delayed response: {actual_duration:.2f}s (requested: {delay_seconds}s)"
        )
