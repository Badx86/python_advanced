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
    """Тесты CRUD операций для ресурсов с проверкой БД"""

    def test_create_resource(self, api_client) -> None:
        """Тест создания ресурса (API + БД)"""
        resource_data = generate_random_resource()
        logger.info(f"Creating resource with data: {resource_data}")

        response = api_client.post("/api/unknown", json=resource_data)
        # Теперь check_create_resource_response автоматически проверяет БД!
        api.check_create_resource_response(response, "/api/unknown", resource_data)
        logger.info("Resource created and verified in database successfully")

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
        """Тест полного обновления ресурса (API + БД)"""
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
        # Теперь check_update_resource_response автоматически проверяет БД!
        api.check_update_resource_response(
            response, f"/api/unknown/{resource_id}", updated_data, resource_id
        )
        logger.info(
            f"Resource {resource_id} updated and verified in database successfully"
        )

    def test_update_resource_patch(self, api_client) -> None:
        """Тест частичного обновления ресурса (API + БД)"""
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
        # Проверяем API + БД
        api.check_update_resource_response(
            response, f"/api/unknown/{resource_id}", updated_data, resource_id
        )
        logger.info(
            f"Resource {resource_id} patched and verified in database successfully"
        )

    def test_delete_resource(self, api_client) -> None:
        """Тест удаления ресурса (API + БД)"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/unknown", json=resource_data)
        created_resource = api.check_create_resource_response(
            create_response, "/api/unknown", resource_data
        )
        resource_id = int(created_resource["id"])

        # Удаляем его
        response = api_client.delete(f"/api/unknown/{resource_id}")
        # Теперь check_delete_resource_response автоматически проверяет БД!
        api.check_delete_resource_response(
            response, f"/api/unknown/{resource_id}", resource_id
        )
        logger.info(
            f"Resource {resource_id} deleted and verified removed from database"
        )

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
        """Тест полного цикла: создание -> проверка -> удаление (с БД проверками)"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/unknown", json=resource_data)
        created_resource = api.check_create_resource_response(
            create_response, "/api/unknown", resource_data
        )
        resource_id = int(created_resource["id"])

        # Проверяем что ресурс существует в БД
        api.check_resource_in_database(resource_id, resource_data)

        # Проверяем что ресурс доступен через API
        get_response = api_client.get(f"/api/unknown/{resource_id}")
        api.check_resource_response(get_response, f"/api/unknown/{resource_id}")

        # Удаляем ресурс
        delete_response = api_client.delete(f"/api/unknown/{resource_id}")
        api.check_delete_resource_response(
            delete_response, f"/api/unknown/{resource_id}", resource_id
        )

        # Проверяем что ресурс удален из API
        get_after_delete = api_client.get(f"/api/unknown/{resource_id}")
        api.check_404_error(get_after_delete, f"/api/unknown/{resource_id}")

        logger.info(
            f"Full CRUD cycle with database verification completed for resource {resource_id}"
        )

    def test_multiple_resources_crud(self, api_client) -> None:
        """Тест создания и удаления нескольких ресурсов"""
        created_resources = []

        # Создаем 3 ресурса
        for i in range(3):
            resource_data = generate_random_resource()
            response = api_client.post("/api/unknown", json=resource_data)
            created_resource = api.check_create_resource_response(
                response, "/api/unknown", resource_data
            )
            created_resources.append((int(created_resource["id"]), resource_data))
            logger.info(f"Created resource {i + 1}/3 with ID {created_resource['id']}")

        # Проверяем что все существуют в БД
        for resource_id, resource_data in created_resources:
            api.check_resource_in_database(resource_id, resource_data)

        # Удаляем все созданные ресурсы
        for resource_id, _ in created_resources:
            response = api_client.delete(f"/api/unknown/{resource_id}")
            api.check_delete_resource_response(
                response, f"/api/unknown/{resource_id}", resource_id
            )
            logger.info(f"Deleted resource {resource_id}")

        logger.info("Multiple resources CRUD test completed successfully")
