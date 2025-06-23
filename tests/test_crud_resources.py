import allure
import logging
import pytest
import random
from mimesis import Text, Numeric
from tests.assertions import APIAssertions

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


@allure.feature("Resources CRUD Operations")
@pytest.mark.crud
class TestResourcesCRUD:
    """Тесты CRUD операций для ресурсов с проверкой БД"""

    @allure.title("Create new resource via API")
    def test_create_resource(self, api_client) -> None:
        """Тест создания ресурса (API + БД)"""
        resource_data = generate_random_resource()
        logger.info(f"Creating resource with data: {resource_data}")

        response = api_client.post("/api/resources", json=resource_data)

        # Логируем curl для документации создания ресурса
        APIAssertions.log_curl_command(response, "📝 Create Resource")

        APIAssertions.check_create_resource_response(
            response, "/api/resources", resource_data
        )
        logger.info("Resource created and verified in database successfully")

    @allure.title("Read existing resource by ID")
    def test_read_resource(self, api_client) -> None:
        """Тест чтения случайного ресурса"""
        # Получаем список ресурсов
        response = api_client.get("/api/resources", params={"page": 1, "size": 50})
        resources_page = APIAssertions.check_resources_list_response(
            response, "/api/resources", page=1, per_page=50
        )

        if resources_page.items:
            # Выбираем случайный ресурс из списка
            random_resource = random.choice(resources_page.items)
            resource_id = random_resource.id

            # Читаем этот случайный ресурс
            response = api_client.get(f"/api/resources/{resource_id}")
            APIAssertions.check_resource_response(
                response, f"/api/resources/{resource_id}"
            )
            logger.info(f"Random resource {resource_id} read successfully")
        else:
            logger.warning("No resources found in database for read test")

    @allure.title("Update resource with PUT method")
    def test_update_resource_put(self, api_client) -> None:
        """Тест полного обновления ресурса (API + БД)"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/resources", json=resource_data)
        created_resource = APIAssertions.check_create_resource_response(
            create_response, "/api/resources", resource_data
        )
        resource_id = int(created_resource["id"])

        # Обновляем его
        updated_data = generate_random_resource()
        logger.info(f"Updating resource {resource_id} with data: {updated_data}")

        response = api_client.put(f"/api/resources/{resource_id}", json=updated_data)

        # Логируем curl для документации обновления ресурса
        APIAssertions.log_curl_command(response, f"🔄 Update Resource {resource_id}")

        APIAssertions.check_update_resource_response(
            response, f"/api/resources/{resource_id}", updated_data, resource_id
        )
        logger.info(
            f"Resource {resource_id} updated and verified in database successfully"
        )

    @allure.title("Update resource with PATCH method")
    def test_update_resource_patch(self, api_client) -> None:
        """Тест частичного обновления ресурса (API + БД)"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/resources", json=resource_data)
        created_resource = APIAssertions.check_create_resource_response(
            create_response, "/api/resources", resource_data
        )
        resource_id = int(created_resource["id"])

        # Обновляем его
        updated_data = generate_random_resource()
        logger.info(f"Patching resource {resource_id} with data: {updated_data}")

        response = api_client.patch(f"/api/resources/{resource_id}", json=updated_data)
        APIAssertions.check_update_resource_response(
            response, f"/api/resources/{resource_id}", updated_data, resource_id
        )
        logger.info(
            f"Resource {resource_id} patched and verified in database successfully"
        )

    @allure.title("Delete resource from system")
    def test_delete_resource(self, api_client) -> None:
        """Тест удаления ресурса (API + БД)"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/resources", json=resource_data)
        created_resource = APIAssertions.check_create_resource_response(
            create_response, "/api/resources", resource_data
        )
        resource_id = int(created_resource["id"])

        # Удаляем его
        response = api_client.delete(f"/api/resources/{resource_id}")

        # Логируем curl для документации удаления ресурса
        APIAssertions.log_curl_command(response, f"🗑️ Delete Resource {resource_id}")

        APIAssertions.check_delete_resource_response(
            response, f"/api/resources/{resource_id}", resource_id
        )
        logger.info(
            f"Resource {resource_id} deleted and verified removed from database"
        )

    @allure.title("Update non-existent resource")
    def test_update_nonexistent_resource(self, api_client) -> None:
        """Тест обновления несуществующего ресурса"""
        updated_data = generate_random_resource()
        logger.info(f"Updating non-existent resource with data: {updated_data}")

        response = api_client.put("/api/resources/999999", json=updated_data)
        # curl автоматически появится при ошибке 404
        APIAssertions.check_404_error(response, "/api/resources/999999")
        logger.info("Non-existent resource correctly failed with 404")

    @allure.title("Delete non-existent resource")
    def test_delete_nonexistent_resource(self, api_client) -> None:
        """Тест удаления несуществующего ресурса"""
        response = api_client.delete("/api/resources/999999")
        # curl автоматически появится при ошибке 404
        APIAssertions.check_404_error(response, "/api/resources/999999")
        logger.info("Non-existent resource DELETE correctly failed with 404")

    @allure.title("Full CRUD cycle for resource")
    def test_create_and_delete_flow(self, api_client) -> None:
        """Тест полного цикла: создание -> проверка -> удаление (с БД проверками)"""
        # Создаем ресурс
        resource_data = generate_random_resource()
        create_response = api_client.post("/api/resources", json=resource_data)
        created_resource = APIAssertions.check_create_resource_response(
            create_response, "/api/resources", resource_data
        )
        resource_id = int(created_resource["id"])

        # Проверяем что ресурс существует в БД
        APIAssertions.check_resource_in_database(resource_id, resource_data)

        # Проверяем что ресурс доступен через API
        get_response = api_client.get(f"/api/resources/{resource_id}")
        APIAssertions.check_resource_response(
            get_response, f"/api/resources/{resource_id}"
        )

        # Удаляем ресурс
        delete_response = api_client.delete(f"/api/resources/{resource_id}")
        APIAssertions.check_delete_resource_response(
            delete_response, f"/api/resources/{resource_id}", resource_id
        )

        # Проверяем что ресурс удален из API
        get_after_delete = api_client.get(f"/api/resources/{resource_id}")
        # curl автоматически появится при ошибке 404
        APIAssertions.check_404_error(get_after_delete, f"/api/resources/{resource_id}")

        logger.info(
            f"Full CRUD cycle with database verification completed for resource {resource_id}"
        )

    @allure.title("Multiple resources CRUD operations")
    def test_multiple_resources_crud(self, api_client) -> None:
        """Тест создания и удаления нескольких ресурсов"""
        created_resources = []

        # Создаем 3 ресурса
        for i in range(3):
            test_resource_data = generate_random_resource()
            response = api_client.post("/api/resources", json=test_resource_data)
            created_resource = APIAssertions.check_create_resource_response(
                response, "/api/resources", test_resource_data
            )
            created_resources.append((int(created_resource["id"]), test_resource_data))
            logger.info(f"Created resource {i + 1}/3 with ID {created_resource['id']}")

        # Проверяем что все существуют в БД
        for resource_id, expected_resource_data in created_resources:
            APIAssertions.check_resource_in_database(
                resource_id, expected_resource_data
            )

        # Удаляем все созданные ресурсы
        for resource_id, _ in created_resources:
            response = api_client.delete(f"/api/resources/{resource_id}")
            APIAssertions.check_delete_resource_response(
                response, f"/api/resources/{resource_id}", resource_id
            )
            logger.info(f"Deleted resource {resource_id}")

        logger.info("Multiple resources CRUD test completed successfully")
