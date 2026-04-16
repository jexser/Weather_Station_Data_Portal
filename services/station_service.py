import errors, validators, constants, repositories.station_repository as station_repo
import pandas as pd
from flask import jsonify, Response
import json


def get_stations_index_page(page_str: str | None = "1") -> str:
    """
    Returns the stations index as a DataFrame with station IDs and names.
    Args:
        page (int): page to be returned
    Returns:
        dict: A subset of the original DataFrame containing only the rows for the requested page; \
            also contains total record before pagination, current page and gape size
    Raises: 
        BadRequest: If page if page is not int or less than 1
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

    json_payload = json.dumps({
        "data": paginated.to_dict(orient="records"),
        "total": lotal_records,
        "page": page_str,
        "page_size": constants.INDEX_PAGE_SIZE,
        "has_next": has_next
    })
    return json_payload


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
    For a date query, returns a dict with stationid, date, and temperature.
    For a year query, returns a list of daily records for that year.
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