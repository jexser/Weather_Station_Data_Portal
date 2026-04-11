class APIError(Exception):
    """Base class for API errors."""
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code

class BadRequest(APIError):
    """Exception raised for bad requests (HTTP 400)."""
    def __init__(self, message: str) -> None:
        self.message = message
        self.status_code = 400

class NotFound(APIError):
    """Exception raised when a resource is not found (HTTP 404)."""
    def __init__(self, message: str) -> None:
        self.message = message
        self.status_code = 404

class InternalServerError(APIError):
    """Exception raised for internal server errors (HTTP 500)."""
    def __init__(self, message: str) -> None:
        self.message = message
        self.status_code = 500