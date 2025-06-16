import logging
import pytest
import random
from mimesis import Text, Numeric
from tests.assertions import api

logger = logging.getLogger(__name__)

# Инициализируем генераторы
text = Text()
numeric = Numeric()


def generate_random_resource():
    """Генерирует случайные тестовые данные ресурса с помощью mimesis"""
    return {
        "name": text.color().lower(),
        "year": numeric.integer_number(2020, 2030),
        "color": text.hex_color(),
        "pantone_value": f"{text.word().upper()}-{numeric.integer_number(100, 999)}",
    }


@pytest.mark.crud
class TestResourcesCRUD:
    """Тесты CRUD операций для ресурсов"""

    def test_create_resource(self, api_client) -> None:
        """Тест создания ресурса"""
        resource_data = generate_random_resource()
        logger.info(f"Creating resource with data: {resource_data}")

        response = api_client.post("/api/unknown", json=resource_data)
        api.check_create_resource_response(response, "/api/unknown", resource_data)
        logger.info("Resource created successfully")

    def test_read_resource(self, api_client) -> None:
        """Тест чтения случайного ресурса"""
        # Получаем список ресурсов
        response = api_client.get("/api/unknown", params={"page": 1, "per_page": 50})
        resources_page = api.check_resources_list_response(
            response, "/api/unknown", page=1, per_page=50
        )

        if resources_page.items:
            # Выбираем случайный ресурс из списка
            random_resource = random.choice(resources_page.items)
            resource_id = random_resource.id

            # Читаем этот случайный ресурс
            response = api_client.get(f"/api/unknown/{resource_id}")
            api.check_resource_response(response, f"/api/unknown/{resource_id}")
            logger.info(f"Random resource {resource_id} read successfully")
        else:
            logger.warning("No resources found in database for read test")

    def test_update_resource_put(self, api_client) -> None:
        """Тест полного обновления ресурса"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/unknown", json=resource_data)
        created_resource = api.check_create_resource_response(
            create_response, "/api/unknown", resource_data
        )
        resource_id = int(created_resource["id"])

        # Обновляем его
        updated_data = generate_random_resource()
        logger.info(f"Updating resource {resource_id} with data: {updated_data}")

        response = api_client.put(f"/api/unknown/{resource_id}", json=updated_data)
        api.check_update_resource_response(
            response, f"/api/unknown/{resource_id}", updated_data
        )
        logger.info(f"Resource {resource_id} updated successfully with PUT")

    def test_update_resource_patch(self, api_client) -> None:
        """Тест частичного обновления ресурса"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/unknown", json=resource_data)
        created_resource = api.check_create_resource_response(
            create_response, "/api/unknown", resource_data
        )
        resource_id = int(created_resource["id"])

        # Обновляем его
        updated_data = generate_random_resource()
        logger.info(f"Patching resource {resource_id} with data: {updated_data}")

        response = api_client.patch(f"/api/unknown/{resource_id}", json=updated_data)
        api.check_update_resource_response(
            response, f"/api/unknown/{resource_id}", updated_data
        )
        logger.info(f"Resource {resource_id} updated successfully with PATCH")

    def test_delete_resource(self, api_client) -> None:
        """Тест удаления ресурса"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/unknown", json=resource_data)
        created_resource = api.check_create_resource_response(
            create_response, "/api/unknown", resource_data
        )
        resource_id = int(created_resource["id"])

        # Удаляем его
        response = api_client.delete(f"/api/unknown/{resource_id}")
        api.check_delete_resource_response(response, f"/api/unknown/{resource_id}")
        logger.info(f"Resource {resource_id} deleted successfully")

    def test_update_nonexistent_resource(self, api_client) -> None:
        """Тест обновления несуществующего ресурса"""
        updated_data = generate_random_resource()
        logger.info(f"Updating non-existent resource with data: {updated_data}")

        response = api_client.put("/api/unknown/999999", json=updated_data)
        api.check_404_error(response, "/api/unknown/999999")
        logger.info("Non-existent resource correctly failed with 404")

    def test_delete_nonexistent_resource(self, api_client) -> None:
        """Тест удаления несуществующего ресурса"""
        response = api_client.delete("/api/unknown/999999")
        api.check_404_error(response, "/api/unknown/999999")
        logger.info("Non-existent resource DELETE correctly failed with 404")

    def test_create_and_delete_flow(self, api_client) -> None:
        """Тест полного цикла: создание -> проверка -> удаление"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/unknown", json=resource_data)
        created_resource = api.check_create_resource_response(
            create_response, "/api/unknown", resource_data
        )
        resource_id = int(created_resource["id"])

        # Проверяем что ресурс существует
        get_response = api_client.get(f"/api/unknown/{resource_id}")
        api.check_resource_response(get_response, f"/api/unknown/{resource_id}")

        # Удаляем ресурс
        delete_response = api_client.delete(f"/api/unknown/{resource_id}")
        api.check_delete_resource_response(
            delete_response, f"/api/unknown/{resource_id}"
        )

        # Проверяем что ресурс удален
        get_after_delete = api_client.get(f"/api/unknown/{resource_id}")
        api.check_404_error(get_after_delete, f"/api/unknown/{resource_id}")

        logger.info(f"Full CRUD cycle completed for resource {resource_id}")
