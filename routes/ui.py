from flask import Blueprint, request, render_template
import services.station_service as station_service
import constants
from models import StationRecord

ui_bp = Blueprint("ui", __name__)


def _present_station_row(station: StationRecord) -> dict:
    return {
        "id": station.station_id,
        "name": station.station_name,
    }


@ui_bp.route("/")
def home():
    page_str = request.args.get("page", "1") # default = 1
    station_name = request.args.get("station_name")

    if station_name:
        search_result = station_service.find_stations_by_name(station_name)
        station_rows = [_present_station_row(station) for station in search_result.stations]
        page = 1
        has_next = False
        total_pages = 1
    else:
        page_result = station_service.get_stations_index_page(page_str=page_str)
        station_rows = [_present_station_row(station) for station in page_result.stations]
        page = page_result.page
        has_next = page_result.has_next
        total_pages = page_result.total_pages

    return render_template(
        "home.html",
        data=station_rows,
        no_results=len(station_rows) == 0,
        page=page,
        has_next=has_next,
        page_size=constants.INDEX_PAGE_SIZE,
        total_pages=total_pages
    )
