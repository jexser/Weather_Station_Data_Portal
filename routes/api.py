from flask import Blueprint, request, jsonify
import services.station_service as station_service
from errors import BadRequest
from models import DailyTemperatureRecord, StationRecord, StationYearlyResult

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


@api_bp.route("/api/v1/stations")
def paginated_station():
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
def get_station_by(stationid: str):
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


@api_bp.route("/api/v1/stations/search")
def find_station_by_name():
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
