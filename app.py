import services.station_service as station_service
import os, logging
from flask import Flask, render_template, request, jsonify, Response
from errors import APIError, BadRequest, jsonify_error
from logging.handlers import RotatingFileHandler
from typing import Final
from dotenv import load_dotenv
import constants
import repositories.station_repository as station_repository
from routes.api import api_bp
from routes.ui import ui_bp

# ===================
# APP INIT
# ===================
load_dotenv()
DEBUG: Final[bool] = str(os.getenv("Debug")).lower() == "true"
LOG_FILE_LOCATION: Final[str] = os.path.join("logs", "app_logs.log")

# Logs
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
handler = RotatingFileHandler(
    LOG_FILE_LOCATION,
    maxBytes=1_048_576,  # 1 MiB
    backupCount=3
)
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[handler, logging.StreamHandler()]
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
# ===================
# END OF APP INIT
# ===================

app = Flask(__name__)
app.register_blueprint(api_bp)
app.register_blueprint(ui_bp)


@app.errorhandler(APIError)
def handle_api_error(error: APIError) -> Response:
    """
    Handles APIError exceptions and returns a JSON response with the error details.
    Args:
        error (APIError): The APIError exception that was raised
    Returns:
        Response: A Flask Response object containing the JSON error message
    """
    return jsonify_error(error)


if __name__ == "__main__":
    station_repository.load_station_index() #preload for caching
    app.run(debug=True if DEBUG else False)