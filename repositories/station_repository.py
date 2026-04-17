import pandas as pd
from functools import lru_cache
from pathlib import Path
import constants
import os, logging
from errors import InternalServerError
import validators
import datetime


@lru_cache(maxsize=128) # Cache results to improve performance for repeated requests
def _load_and_clean_data(
        file_path: Path,
        rows_to_skip: int = 0,
        parse_dates: bool = False
        ) -> pd.DataFrame:
    """
    Loads an ECA&D-format CSV file and applies standard cleaning steps.
    Column name whitespace is stripped. If a TG column is present, -9999 sentinels
    are replaced with pd.NA and values are divided by 10 to convert from tenths of
    degrees Celsius to degrees Celsius. Dates are optionally parsed to datetime.
    Args:
        file_path (Path): The path to the CSV file to be loaded.
        rows_to_skip (int): The number of header rows to skip. Default is 0.
        parse_dates (bool): Whether to parse the DATE column to datetime. Default is False.
    Returns:
        pd.DataFrame: Cleaned DataFrame ready for analysis or further processing.
    """
    df = pd.read_csv(
        file_path, 
        skiprows=rows_to_skip
        )
    df.columns = df.columns.str.strip() # Remove leading/trailing whitespace from column names
    if constants.FIELD_TG in df.columns:
        df[constants.FIELD_TG] = df[constants.FIELD_TG].replace(-9999, pd.NA) # Replace -9999 with NaN for better handling of missing data
        df[constants.FIELD_TG] = df[constants.FIELD_TG] / 10 # Convert temperature from tenths of degrees to degrees Celsius
    if parse_dates:
        df[constants.FIELD_DATE] = pd.to_datetime(df[constants.FIELD_DATE], format="%Y%m%d", errors='coerce') # type: ignore
    return df


def _load_station_index() -> pd.DataFrame:
    """
    Loads the stations index file and returns a cleaned DataFrame with station IDs and names.
    Returns:
        pd.DataFrame: DataFrame with STAID and STANAME columns; station names are stripped of whitespace.
    Raises:
        InternalServerError: If the stations index file is not found on disk.
    """
    index_file_path = constants.DATA_DIR / "stations.txt"
    if not os.path.exists(path=index_file_path):
        logging.critical(f"Stations index file not found at path: {index_file_path}")
        raise InternalServerError("Stations index data not found.")
        
    stations = _load_and_clean_data(
        index_file_path, 
        rows_to_skip=constants.ROWS_TO_SKIP_INDEX, 
        parse_dates=False
        )
    stations = stations[[constants.FIELD_STAID, constants.FIELD_STANAME]] #filter and leave only two fields we need to render
    stations[constants.FIELD_STANAME] = stations[constants.FIELD_STANAME].str.strip()
    return stations


def get_station_index() -> list:
    """
    Returns the full station index as a list of dicts with STAID and STANAME keys.
    Returns:
        list: All station records from the index file.
    Raises:
        InternalServerError: If the stations index file is not found on disk.
    """
    return _load_station_index().to_dict(orient="records")


def _load_station(stationid: str) -> pd.DataFrame:
    """
    Loads a station's temperature data file and returns a cleaned DataFrame.
    Args:
        stationid (str): The station ID used to locate the file (e.g. "1" resolves to TG_STAID000001.txt).
    Returns:
        pd.DataFrame: Cleaned DataFrame with DATE (datetime) and TG (°C) columns.
    Raises:
        BadRequest: If the station ID format is invalid.
        NotFound: If no data file exists for the given station ID.
    """
    validators.validate_station_id(stationid)
    station_file_path = constants.DATA_DIR / f"TG_STAID{stationid.zfill(6)}.txt"
    validators.validate_file_existence(station_file_path)

    return _load_and_clean_data(
        file_path=station_file_path, 
        rows_to_skip=constants.ROWS_TO_SKIP_STATION, 
        parse_dates=True
        )


def get_station(stationid: str) -> list:
    """
    Returns all daily records for a station as a list of dicts.
    Args:
        stationid (str): The station ID (e.g. "1" resolves to TG_STAID000001.txt).
    Returns:
        list: All records with DATE (datetime) and TG (°C) keys.
    Raises:
        BadRequest: If the station ID format is invalid.
        NotFound: If no data file exists for the given station ID.
    """
    return _load_station(stationid=stationid).to_dict(orient="records")

def extract_temperature(stationid: str, date: datetime.datetime) -> float:
    """
    Returns the temperature for a station on a specific date.
    Args:
        stationid (str): The station ID to query.
        date (datetime.datetime): The exact date to look up.
    Returns:
        float: Temperature in degrees Celsius for the given date.
    Raises:
        BadRequest: If the station ID format is invalid or temperature data is missing/invalid.
        NotFound: If no data file exists for the given station ID.
    """
    df = _load_station(stationid)
    temperature_series = df.loc[df[constants.FIELD_DATE] == date][constants.FIELD_TG].squeeze()
    temperature = validators.validate_temperature_data(temperature_series)
    return temperature

def extract_temperature_series(stationid: str, year_str: str) -> list[dict]:
    """
    Returns all daily records for a station in a given year.
    Args:
        stationid (str): The station ID to query.
        year_str (str): The year to filter by in YYYY format.
    Returns:
        list[dict]: Daily records for the year, each with DATE (datetime) and TG (°C) keys.
            Returns an empty list if no data exists for that year.
    Raises:
        BadRequest: If the station ID format is invalid.
        NotFound: If no data file exists for the given station ID.
    """
    df = _load_station(stationid)
    station_data = df.loc[df[constants.FIELD_DATE].dt.year == int(year_str)].to_dict(orient="records")
    return station_data

    
def search_stations_by_name(query: str) -> list[dict]:
    """
    Searches the station index for stations whose names contain the given query string.
    Args:
        query (str): Case-insensitive substring to match against station names.
    Returns:
        list[dict]: Matching station records, each with STAID and STANAME keys.
            Returns an empty list if no stations match.
    Raises:
        InternalServerError: If the stations index file is not found on disk.
    """
    df = _load_station_index()
    search_results = df.loc[
        df[constants.FIELD_STANAME].str.contains(query, case=False, na=False, regex=False)
    ]

    return search_results.to_dict(orient="records")