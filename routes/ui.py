from flask import Blueprint, request, render_template
import services.station_service as station_service
import services.handlers as handlers
import constants
from models import StationRecord

ui_bp = Blueprint("ui", __name__)


def _present_station_row(station: StationRecord) -> dict:
    return {
        "id": station.station_id,
        "name": station.station_name,
    }


@ui_bp.route("/")
def home_ui():
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
        data = station_rows,
        no_results = len(station_rows) == 0,
        page = page,
        has_next = has_next,
        page_size = constants.INDEX_PAGE_SIZE,
        total_pages = total_pages
    )


@ui_bp.route("/insights")
def insights_ui():
    stationid = request.args.get("station_id")
    date = request.args.get("date_input")

    if stationid:
        hottest_year = handlers._get_hottest_year(stationid, date_mm_dd=date)["data"]["year"]
        coldest_year = handlers._get_coldest_year(stationid, date_mm_dd=date)["data"]["year"]
        hottest_day = handlers._get_hottest_day(stationid, date_mm_dd=date)["data"]["date"]
        coldest_day = handlers._get_coldest_day(stationid, date_mm_dd=date)["data"]["date"]
        missing_record = std_temp = handlers._get_missing_data_count(stationid, date_mm_dd=date)["data"]["missing_count"]
        # if date:
        #     avg_temp = handlers._get_avg_for_date(stationid, date_mm_dd=date)["data"]["avg_temp"]
        #     std_temp = handlers._get_avg_for_date(stationid, date_mm_dd=date)["data"]["std_dev"]
        # else:
        #     avg_temp = ""
        #     std_temp = ""

        return render_template(
            "insights.html",
            hottest_year = hottest_year,
            coldest_year = coldest_year,
            hottest_day = hottest_day,
            coldest_day = coldest_day,
            # avg_temp = avg_temp,
            # std_temp = std_temp,
            missing_records = missing_record
        )
    else:
        return render_template("insights.html") # TODO: add error/empy data handling


@ui_bp.route("/error")
def internal_error_ui():
    return render_template("error.html")