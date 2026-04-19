import os, logging
from flask import Flask, render_template
from errors import APIError, InternalServerError, jsonify_error
from logging.handlers import RotatingFileHandler
from typing import Final
from dotenv import load_dotenv
import repositories.station_repository as station_repository
from routes.api import api_bp
from routes.ui import ui_bp
from werkzeug.exceptions import HTTPException

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
def handle_api_error(error: APIError):
    if isinstance(error, InternalServerError):
        logging.error(f"500: {error.message}")
        return render_template("error.html"), 500
    return jsonify_error(error)


@app.errorhandler(Exception)
def handle_unexpected_error(error: Exception):
    if isinstance(error, HTTPException):
        return error
    app.logger.error("Unhandled exception: %s", error)
    return render_template("error.html"), 500


if __name__ == "__main__":
    station_repository._load_station_index() #preload for caching
    app.run(debug=True if DEBUG else False)