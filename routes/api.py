from flask import Blueprint, request, jsonify
import services.station_service as station_service
from errors import BadRequest
from models import DailyTemperatureRecord, StationComparisonRecord, StationRecord, StationYearlyResult, YearlyTemperatureRecord

api_bp = Blueprint("api", __name__)


def _serialize_station(station: StationRecord) -> dict:
    return {
        "STAID": station.station_id,
        "STANAME": station.station_name,
    }


def _serialize_daily_temperature(record: DailyTemperatureRecord) -> dict:
    return {
        "date": record.date,
        "temperature": record.temperature,
    }


def _serialize_yearly_average(record: YearlyTemperatureRecord) -> dict:
    return {
        "year": record.year,
        "temperature": record.temperature,
    }


def _serialize_station_comparison(record: StationComparisonRecord) -> dict:
    return {
        "date": record.date,
        "stationA": record.station_a,
        "stationB": record.station_b,
    }


@api_bp.route("/api/v1/stations")
def paginated_station_api():
    page = request.args.get("page", "1")
    result = station_service.get_stations_index_page(page_str=page)
    
    return jsonify({
        "data": [_serialize_station(station) for station in result.stations],
        "items": result.total_items,
        "page": result.page,
        "page_size": result.page_size,
        "total_pages": result.total_pages,
        "has_next": result.has_next
    })


@api_bp.route("/api/v1/station/<stationid>")
def get_station_by_id_api(stationid: str):
    year_str = request.args.get("year")
    date_str = request.args.get("date")

    result = station_service.get_station_data_by_date_or_year(stationid, date_str, year_str)

    if isinstance(result, StationYearlyResult):
        data = [_serialize_daily_temperature(record) for record in result.records]
        items = len(result.records)
    else:
        data = {
            "stationid": result.station_id,
            "date": result.date,
            "temperature": result.temperature,
        }
        items = 1
    
    return jsonify({
        "data": data,
        "items": items
    })


@api_bp.route("/api/v1/station/<stationid>/yearly")
def get_station_yearly_averages_api(stationid: str):
    result = station_service.get_station_yearly_averages(stationid)
    return jsonify({
        "data": [_serialize_yearly_average(r) for r in result.records],
        "items": len(result.records),
        "stationid": result.station_id,
    })


@api_bp.route("/api/v1/station/<stationid>/date/<mm_dd>")
def get_station_date_across_years_api(stationid: str, mm_dd: str):
    result = station_service.get_station_temperature_for_date(stationid, mm_dd)
    return jsonify({
        "data": [_serialize_daily_temperature(r) for r in result.records],
        "items": len(result.records),
        "stationid": result.station_id,
        "mm_dd": result.mm_dd,
    })


@api_bp.route("/api/v1/stations/search")
def find_station_by_name_api():
    name_str = request.args.get("name")

    if name_str:
        result = station_service.find_stations_by_name(name_str)
        return jsonify({
            "data": [_serialize_station(station) for station in result.stations],
            "search_query": result.query,
            "items": len(result.stations)
        })
    else:
        raise BadRequest("No value for param 'name' is provided")
    

@api_bp.route("/api/v1/insights/<stationid>")
def get_station_insight_api(stationid: str):
    insight_type = request.args.get("type")
    date = request.args.get("date")

    if not insight_type:
        raise BadRequest("Parameter 'type' is required.")
    payload = station_service.get_insight_for_station(stationid, insight_type, date)

    return jsonify(payload)


@api_bp.route("/api/v1/compare")
def compare_stations_api():
    station_a_id = request.args.get("stationA_id")
    station_b_id = request.args.get("stationB_id")
    year = request.args.get("year")

    if not station_a_id:
        raise BadRequest("Parameter 'stationA_id' is required.")
    if not station_b_id:
        raise BadRequest("Parameter 'stationB_id' is required.")
    if not year:
        raise BadRequest("Parameter 'year' is required.")

    result = station_service.get_station_comparison(
        station_a_id=station_a_id,
        station_b_id=station_b_id,
        year_str=year,
    )

    return jsonify({
        "data": [_serialize_station_comparison(record) for record in result.records],
        "items": len(result.records),
        "stationA_id": result.station_a_id,
        "stationB_id": result.station_b_id,
        "year": result.year,
    })
