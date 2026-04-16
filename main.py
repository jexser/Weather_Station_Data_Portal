import services.station_service as station_service
import os, logging
from flask import Flask, render_template, request, jsonify, Response
from errors import APIError, InternalServerError, jsonify_error
from logging.handlers import RotatingFileHandler
from typing import Final
from dotenv import load_dotenv
import json
import constants

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

app = Flask(__name__)
# ===================
# END OF APP INIT
# ===================


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


@app.route("/")
def home():
    page_str = request.args.get("page", "1") # default = 1
    stations = station_service.get_stations_index_page(page_str=page_str)
    data: list = stations["data"]
    has_next = stations["has_next"]

    return render_template(
        "home.html", 
        data=data, 
        page=int(page_str),
        has_next=has_next,
        page_size=constants.INDEX_PAGE_SIZE
    )


@app.route("/api/v1/stations")
def paginated_station():
    page = request.args.get("page")
    stations = station_service.get_stations_index_page(page_str=page)
    
    return jsonify({
        "data": stations["data"],
        "total": stations["total"],
        "page": stations["page"],
        "page_size": stations["page_size"],
        "has_next": stations["has_next"]
    })


@app.route("/api/v1/station/<stationid>")
def get_station_by(stationid: str):
    year_str = request.args.get("year")
    date_str = request.args.get("date")
    
    return jsonify(station_service.get_by_date_or_year(stationid, date_str, year_str))


if __name__ == "__main__":
    app.run(debug=True if DEBUG else False)