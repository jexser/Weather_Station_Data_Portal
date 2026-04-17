from flask import Blueprint, request, render_template
import services.station_service as station_service
import constants
import os

ui_bp = Blueprint("ui", __name__)


@ui_bp.route("/")
def home():
    page_str = request.args.get("page", "1") # default = 1
    station_name = request.args.get("station_name")

    if station_name:
        stations = station_service.find_stations_by_name(station_name)
        data = stations["data"]
    else:
        stations = station_service.get_stations_index_page(page_str=page_str)
        data: list = stations["data"]
        
    has_next = stations["has_next"]
    total_pages = stations["total_pages"]

    return render_template(
        "home.html",
        data=data, 
        page=int(page_str),
        has_next=has_next,
        page_size=constants.INDEX_PAGE_SIZE,
        total_pages=total_pages
    )