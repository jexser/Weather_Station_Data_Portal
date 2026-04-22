import math

import constants
import errors
import repositories.station_repository as station_repo
import validators
from models import (
    PaginatedStations,
    StationSearchResult,
    StationTemperatureResult,
    StationYearlyResult,
)
import services.handlers as handlers


INSIGHT_HANDLERS = {
    "hottest_year": handlers._get_hottest_year,
    "coldest_year": handlers._get_coldest_year,
    "hottest_day": handlers._get_hottest_day,
    "coldest_day": handlers._get_coldest_day,
    "avg_for_date": handlers._get_avg_for_date,
    "temp_variability": handlers._get_temp_variability,
    "missing_data_count": handlers._get_missing_data_count,
    }


def get_stations_index_page(page_str: str | None = "1") -> PaginatedStations:
    """
    Returns a paginated station index result using domain-oriented fields.
    """
    page = validators.validate_page_number(page_str)
    stations = station_repo.get_station_index()
    total_items = len(stations)
    paginated_stations = _paginate_index(
        stations,
        page=page,
        page_size=constants.INDEX_PAGE_SIZE,
    )

    total_pages = math.ceil(total_items / constants.INDEX_PAGE_SIZE) if total_items else 1
    has_next = page < total_pages

    return PaginatedStations(
        stations=tuple(paginated_stations),
        page=page,
        page_size=constants.INDEX_PAGE_SIZE,
        total_items=total_items,
        total_pages=total_pages,
        has_next=has_next,
    )


def find_stations_by_name(station_name: str) -> StationSearchResult:
    """
    Returns a domain result for station-name search.
    """
    validators.validate_station_name(station_name=station_name)

    search_results = station_repo.search_stations_by_name(station_name)
    limited_results = search_results[: constants.SEARCH_RESULTS_LIMIT]

    return StationSearchResult(
        query=station_name,
        stations=tuple(limited_results),
        limit=constants.SEARCH_RESULTS_LIMIT,
    )


def get_station_data_by_date_or_year(
    stationid: str,
    date_str: str | None,
    year_str: str | None,
) -> StationTemperatureResult | StationYearlyResult:
    """
    Returns temperature data for a station filtered by a specific date or year.
    """
    validators.validate_date_and_year_args(date_str, year_str)

    if date_str:
        parsed_date = validators.validate_date_format(date_str)
        temperature = station_repo.extract_temperature(stationid=stationid, date=parsed_date)
        return StationTemperatureResult(
            station_id=stationid,
            date=date_str,
            temperature=temperature,
        )

    if year_str:
        validators.validate_year_format(year_str)
        records = station_repo.extract_temperature_series(stationid=stationid, year_str=year_str)
        return StationYearlyResult(
            station_id=stationid,
            year=year_str,
            records=tuple(records),
        )

    raise errors.BadRequest("Either date or year must be provided")


def _paginate_index(data: list, page: int, page_size: int = 500) -> list:
    """
    Returns a page-sized slice of a list based on the page number and page size.
    """
    starting_item = (page - 1) * page_size
    ending_item = page * page_size
    return data[starting_item:ending_item]


def get_insight_for_station(stationid: str, insight_type: str, date: str | None):
    # "hottest_year"
    # "coldest_year"
    # "hottest_day"
    # "coldest_day"
    # "avg_for_date"
    # "temp_variability"
    # "missing_data_count"

    handler = INSIGHT_HANDLERS.get(insight_type)

    if not handler:
        raise errors.BadRequest("Invalid insight type")

    return handler(stationid, date)