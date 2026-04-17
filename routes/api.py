from flask import Blueprint, request, jsonify
import services.station_service as station_service
from errors import BadRequest

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/v1/stations")
def paginated_station():
    page = request.args.get("page", "1")
    stations = station_service.get_stations_index_page(page_str=page)
    
    return jsonify({
        "data": stations["data"],
        "items": stations["items"],
        "page": stations["page"],
        "page_size": stations["page_size"],
        "total_pages": stations["total_pages"],
        "has_next": stations["has_next"]
    })


@api_bp.route("/api/v1/station/<stationid>")
def get_station_by(stationid: str):
    year_str = request.args.get("year")
    date_str = request.args.get("date")

    station_data = station_service.get_by_date_or_year(stationid, date_str, year_str)
    items = len(station_data)
    
    return jsonify({
        "data": station_data,
        "items": items
    })


@api_bp.route("/api/v1/stations/search")
def find_station_by_name():
    name_str = request.args.get("name")

    if name_str:
        result = station_service.find_stations_by_name(name_str)
        return jsonify({
            "data": result["data"],
            "search_query": result["search_query"],
            "items": result["items"]
        })
    else:
        raise BadRequest("No value for param 'name' is provided")