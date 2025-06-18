from fastapi import HTTPException
from http import HTTPStatus


class APIException(HTTPException):
    """Унифицированный exception для API с консистентным форматом ошибок"""

    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail={"error": message})


class UserNotFoundError(APIException):
    """Пользователь не найден"""

    def __init__(self, user_id: int):
        super().__init__(HTTPStatus.NOT_FOUND, f"User {user_id} not found")


class ResourceNotFoundError(APIException):
    """Ресурс не найден"""

    def __init__(self, resource_id: int):
        super().__init__(HTTPStatus.NOT_FOUND, f"Resource {resource_id} not found")


class ValidationError(APIException):
    """Ошибка валидации данных"""

    def __init__(self, message: str):
        super().__init__(HTTPStatus.BAD_REQUEST, message)


class InvalidIDError(APIException):
    """Невалидный ID"""

    def __init__(self, entity: str = "ID"):
        super().__init__(HTTPStatus.UNPROCESSABLE_ENTITY, f"Invalid {entity}")
