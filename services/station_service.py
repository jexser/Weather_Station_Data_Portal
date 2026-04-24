import datetime
import math

import constants
import errors
import repositories.station_repository as station_repository
import validators
from models import (
    PaginatedStations,
    StationComparisonRecord,
    StationComparisonResult,
    StationDateAcrossYearsResult,
    StationSearchResult,
    StationTemperatureResult,
    StationYearlyAveragesResult,
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
    stations = station_repository.get_station_index()
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

    search_results = station_repository.search_stations_by_name(station_name)
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
        temperature = station_repository.extract_temperature(stationid=stationid, date=parsed_date)
        return StationTemperatureResult(
            station_id=stationid,
            date=date_str,
            temperature=temperature,
        )

    if year_str:
        validators.validate_year_format(year_str)
        records = station_repository.extract_temperature_series(stationid=stationid, year_str=year_str)
        return StationYearlyResult(
            station_id=stationid,
            year=year_str,
            records=tuple(records),
        )

    raise errors.BadRequest("Either date or year must be provided")


def get_station_yearly_averages(stationid: str) -> StationYearlyAveragesResult:
    validators.validate_station_id(stationid)
    records = station_repository.extract_yearly_averages(stationid)
    return StationYearlyAveragesResult(
        station_id=stationid,
        records=tuple(records),
    )


def get_station_temperature_for_date(stationid: str, mm_dd: str) -> StationDateAcrossYearsResult:
    validators.validate_station_id(stationid)
    validators.validate_mm_dd_date_format(mm_dd)
    records = station_repository.extract_temperature_series_for_date(stationid, mm_dd)
    return StationDateAcrossYearsResult(
        station_id=stationid,
        mm_dd=mm_dd,
        records=tuple(records),
    )


def _paginate_index(data: list, page: int, page_size: int = 500) -> list:
    """
    Returns a page-sized slice of a list based on the page number and page size.
    """
    starting_item = (page - 1) * page_size
    ending_item = page * page_size
    return data[starting_item:ending_item]


def get_insight_for_station(stationid: str, insight_type: str, date: str | None) -> dict:
    """
    Dispatches to the appropriate insight handler based on insight_type.

    Raises BadRequest for unsupported types. Date-dependent handlers
    (avg_for_date, temp_variability) raise BadRequest internally if date is absent.
    """
    validators.validate_insight_params(insight_type=insight_type, date_str=date)

    handler = INSIGHT_HANDLERS[insight_type]
    return handler(stationid, date)


def get_station_comparison(
    station_a_id: str,
    station_b_id: str,
    year_str: str,
) -> StationComparisonResult:
    """
    Returns a full-year date union for two stations in the given year.
    """
    validators.validate_station_id(station_a_id)
    validators.validate_station_id(station_b_id)
    validators.validate_year_format(year_str)

    station_a_records = _get_station_yearly_records_or_raise(station_a_id, year_str, "stationA_id")
    station_b_records = _get_station_yearly_records_or_raise(station_b_id, year_str, "stationB_id")

    station_a_by_date = {record.date: record.temperature for record in station_a_records}
    station_b_by_date = {record.date: record.temperature for record in station_b_records}

    year = int(year_str)
    current_date = datetime.date(year, 1, 1)
    last_date = datetime.date(year, 12, 31)
    comparison_rows: list[StationComparisonRecord] = []

    while current_date <= last_date:
        date_key = current_date.isoformat()
        comparison_rows.append(
            StationComparisonRecord(
                date=date_key,
                station_a=station_a_by_date.get(date_key),
                station_b=station_b_by_date.get(date_key),
            )
        )
        current_date += datetime.timedelta(days=1)

    return StationComparisonResult(
        station_a_id=station_a_id,
        station_b_id=station_b_id,
        year=year_str,
        records=tuple(comparison_rows),
    )


def _get_station_yearly_records_or_raise(
    station_id: str,
    year_str: str,
    param_name: str,
):
    try:
        result = get_station_data_by_date_or_year(
            stationid=station_id,
            date_str=None,
            year_str=year_str,
        )
    except errors.NotFound as exc:
        raise errors.NotFound(f"Station data not found for {param_name}={station_id}.") from exc

    if not isinstance(result, StationYearlyResult):
        raise errors.InternalServerError("Unexpected comparison result type.")

    return result.records
