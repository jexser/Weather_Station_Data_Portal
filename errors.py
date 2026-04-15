from flask import jsonify, Response

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

def jsonify_error(error: APIError) -> Response:
    """
    Helper function to create a JSON response for errors.
    Args:
        error (APIError): The error object containing the message and status code.
    Returns:
        A JSON response with the error message and appropriate HTTP status code.
    """

    response = jsonify({
        "error": {
            "status_code": error.status_code,
            "message": error.message
        }
    })
    response.status_code = error.status_code
    return response