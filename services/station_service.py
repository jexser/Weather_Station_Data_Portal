import errors, validators, constants, repositories.station_repository as station_repo
import pandas as pd
import math


def get_stations_index_page(page_str: str | None = "1") -> dict:
    """
    Returns a paginated page of the stations index.
    Args:
        page_str (str | None): The page number as a string. Defaults to "1".
    Returns:
        dict: Contains the paginated station records under "data", total record count,
            current page, page size, and a "has_next" flag.
    Raises:
        BadRequest: If page_str is not a valid integer or is less than 1.
    """
    page: int = validators.validate_page_number(page_str)
    stations: list = station_repo.get_station_index()
    total_records: int = len(stations)
    paginated: list = _paginate_index(stations, page=page, page_size=constants.INDEX_PAGE_SIZE)

    remainder: int = total_records - (page * constants.INDEX_PAGE_SIZE)
    total_pages: int = math.ceil(total_records / constants.INDEX_PAGE_SIZE)
    has_next: bool = remainder > 0 

    payload = {
        "data": paginated,
        "items": total_records,
        "page": page,
        "page_size": constants.INDEX_PAGE_SIZE,
        "total_pages": total_pages,
        "has_next": has_next
    }
    return payload


def find_stations_by_name(station_name: str) -> dict:
    """
    Searches the station index for stations whose names contain the given search term.
    Results are capped at MAX_SEARCH_RESULTS if there are too many matches.
    Args:
        station_name (str): The search term to match against station names.
    Returns:
        dict: Contains matched station records under "data", the original search term
            under "search_word", and the number of results under "search_results".
            If no matches are found, "data" is the string "No stations found".
    Raises:
        BadRequest: If station_name contains invalid characters.
    """
    validators.validate_station_name(station_name=station_name)
    
    search_results = station_repo.search_stations_by_name(station_name)
    items = len(search_results)

    if items == 0:
        search_results = "No stations found"
    elif items > constants.MAX_SEARCH_RESULTS:
        search_results = search_results[0:constants.MAX_SEARCH_RESULTS]
        items = len(search_results)

    payload = {
        "data": search_results,
        "search_query": station_name,
        "items": items,
        "page": 1, # Always one as per spec, no calculation needed
        "page_size": constants.MAX_SEARCH_RESULTS,
        "total_pages": 1, # Always one as per spec, no calculation needed
        "has_next": False,
    }

    return payload


def get_station_data_by_date_or_year(stationid: str, date_str: str | None, year_str: str | None) -> dict | list:
    """
    Returns temperature data for a station filtered by a specific date or year.
    Exactly one of date_str or year_str must be provided.
    Args:
        stationid (str): The station ID to query.
        date_str (str | None): A date string in YYYY-MM-DD format, or None.
        year_str (str | None): A year string in YYYY format, or None.
    Returns:
        dict: For a date query — contains stationid, date, and temperature.
        list: For a year query — a list of daily records for that year; empty list if no data.
    Raises:
        BadRequest: If both or neither of date_str and year_str are provided, or if formats are invalid.
        NotFound: If the station file does not exist.
    """
    validators.validate_date_and_year_args(date_str, year_str)
    df = station_repo.load_station(stationid)
    result = {}

    if date_str:
        parsed_date = validators.validate_date_format(date_str)
        temperature_series = df.loc[df[constants.FIELD_DATE] == parsed_date][constants.FIELD_TG].squeeze()
        temperature = validators.validate_temperature_data(temperature_series)

        result = {
            "stationid": stationid,
            "date": date_str, 
            "temperature": temperature
        }
    elif year_str:
        validators.validate_year_format(year_str)
        result = df.loc[df[constants.FIELD_DATE].dt.year == int(year_str)].to_dict(orient="records")
    else:
        raise errors.BadRequest("Either date or year must be provided")

    return result


def _paginate_index(data: list, page: int, page_size: int = 500) -> list:
    """
    Returns a page-sized slice of a list based on the page number and page size.
    Args:
        data (list): The list to paginate.
        page (int): The current page number (1-indexed).
        page_size (int, optional): The maximum number of records per page. Defaults to 500.
    Returns:
        list: A slice of data containing only the records for the requested page.
    """
    starting_item: int = (page - 1) * page_size
    ending_item: int = page * page_size
    return data[starting_item:ending_item]