import errors, validators, constants, repositories.station_repository as station_repo
import pandas as pd


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
    page = validators.validate_page_number(page_str)
    stations = station_repo.load_station_index()
    lotal_records = len(stations)
    if lotal_records > constants.INDEX_PAGE_SIZE:
        paginated = _paginate_index(
            stations, 
            page = page, 
            page_size = constants.INDEX_PAGE_SIZE
        )
    else:
        paginated = stations

    remainder = lotal_records - (page * constants.INDEX_PAGE_SIZE)
    has_next: bool = remainder > 0 

    payload = {
        "data": paginated.to_dict(orient="records"),
        "items": lotal_records,
        "page": page,
        "page_size": constants.INDEX_PAGE_SIZE,
        "has_next": has_next
    }
    return payload


def _paginate_index(df: pd.DataFrame, page: int, page_size: int = 500) -> pd.DataFrame:
    """
    Paginates a DataFrame by returning a specific slice of rows based on the page number and page size.
    Args:
        df (pd.DataFrame): The DataFrame to be paginated.
        page (int): The current page number (1-indexed).
        page_size (int, optional): The maximum number of records to include per page. Defaults to 500.
    Returns:
        pd.DataFrame: A subset of the original DataFrame containing only the rows for the requested page.
    """
    starting_item = (page - 1) * page_size
    ending_item = page * page_size
    return df.iloc[starting_item:ending_item]


def get_by_date_or_year(stationid: str, date_str: str | None, year_str: str | None) -> dict | list:
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
        #if no data, it will return an empty list, which is appropriate for this case
    else:
        raise errors.BadRequest("Either date or year must be provided")

    return result


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

    df = station_repo.load_station_index().copy()
    search_result = df.loc[df[constants.FIELD_STANAME].str.contains(station_name, case=False)].to_dict(orient="records")
    items = len(search_result)

    if items == 0:
        search_result = "No stations found"
    elif items > constants.MAX_SEARCH_RESULTS:
        search_result = search_result[0:constants.MAX_SEARCH_RESULTS]
        items = len(search_result)

    payload = {
        "data": search_result,
        "search_query": station_name,
        "items": items,
        "has_next": False
    }
    return payload