from flask import Blueprint, request, render_template
import services.station_service as station_service
import services.handlers as handlers
import repositories.station_repository as station_repository
import constants
from models import StationRecord

ui_bp = Blueprint("ui", __name__)


def _present_station_row(station: StationRecord) -> dict:
    return {
        "id": station.station_id,
        "name": station.station_name,
    }


def _find_station_name_by_id(station_id: str) -> str:
    for station in station_repository.get_station_index():
        if station.station_id == station_id:
            return station.station_name
    return station_id


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
    station_name = request.args.get("station_name")
    stationid = request.args.get("station_id")
    date = request.args.get("date")

    if stationid:
        if date:
            avg_temp = handlers._get_avg_for_date(stationid, date_mm_dd=date)["data"]["avg_temp"]
            std_temp = handlers._get_temp_variability(stationid, date_mm_dd=date)["data"]["std_dev"]
        else:
            avg_temp = ""
            std_temp = ""

        return render_template(
            "insights.html",
            station_name = station_name,
            stationid = stationid,
            date = date,
            hottest_year = handlers._get_hottest_year(stationid, date_mm_dd=date)["data"]["year"],
            hottest_year_temp = handlers._get_hottest_year(stationid, date_mm_dd=date)["data"]["value"],
            coldest_year = handlers._get_coldest_year(stationid, date_mm_dd=date)["data"]["year"],
            coldest_year_temp = handlers._get_coldest_year(stationid, date_mm_dd=date)["data"]["value"],
            hottest_day = handlers._get_hottest_day(stationid, date_mm_dd=date)["data"]["date"],
            hottest_day_temp = handlers._get_hottest_day(stationid, date_mm_dd=date)["data"]["value"],
            coldest_day = handlers._get_coldest_day(stationid, date_mm_dd=date)["data"]["date"],
            coldest_day_temp = handlers._get_coldest_day(stationid, date_mm_dd=date)["data"]["value"],
            avg_temp = avg_temp,
            std_temp = std_temp,
            missing_records = handlers._get_missing_data_count(stationid, date_mm_dd=date)["data"]["missing_count"]
        )
    else:
        return render_template("insights.html") # TODO: add error/empy data handling


@ui_bp.route("/compare")
def compare_ui():
    station_a_id = request.args.get("station_a_id")
    station_b_id = request.args.get("station_b_id")
    year = request.args.get("year")

    if station_a_id and station_b_id and year:
        comparison = station_service.get_station_comparison(
            station_a_id=station_a_id,
            station_b_id=station_b_id,
            year_str=year,
        )
        return render_template(
            "compare.html",
            station_a_id=station_a_id,
            station_b_id=station_b_id,
            station_a_name=_find_station_name_by_id(station_a_id),
            station_b_name=_find_station_name_by_id(station_b_id),
            year=year,
            records=comparison.records,
        )

    return render_template("compare.html", records=())


@ui_bp.route("/charts")
def charts_ui():
    station_name = request.args.get("station_name", "")
    station_id = request.args.get("station_id", "")
    chart_type = request.args.get("chart_type", "yearly_trend")
    date = request.args.get("date", "")
    return render_template(
        "charts.html",
        station_name=station_name,
        station_id=station_id,
        chart_type=chart_type,
        date=date,
    )


@ui_bp.route("/api")
def api_docs_ui():
    return render_template("api.html")


@ui_bp.route("/error")
def internal_error_ui():
    return render_template("error.html")
