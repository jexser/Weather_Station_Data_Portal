import pandas as pd
from functools import lru_cache
import constants
import os, logging
from errors import InternalServerError
import validators


@lru_cache(maxsize=128) # Cache results to improve performance for repeated requests
def _load_and_clean_data(
        file_path: str, 
        rows_to_skip: int = 0, 
        parse_dates: bool = False
        ) -> pd.DataFrame:
    """
    Loads a CSV file, skipping a specified number of rows (0 by default)
    Optionally, parses the date column. 
    Removes any leading or trailing whitespace from the column names.
    Args:
        file_path (str): The path to the CSV file to be loaded.
        rows_to_skip (int): The number of rows to skip at the beginning of the file. Default is 0.
        parse_dates (bool): Whether to parse the date column. Default is False.
    Returns:
        pd.DataFrame: cleaned DataFrame ready for analysis or further processing.
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


def load_station_index() -> pd.DataFrame:
    """
    Loads the stations index CSV file and returns a DataFrame with station IDs and names.
    """
    index_file_path = os.path.join(os.getcwd(), "data", "stations.txt")
    if not os.path.exists(path=index_file_path):
        logging.critical(f"Stations index file not found at path: {index_file_path}")
        raise InternalServerError("Stations index data not found.")
        
    stations = _load_and_clean_data(index_file_path, 
                                    rows_to_skip=constants.ROWS_TO_SKIP_INDEX, 
                                    parse_dates=False)
    stations = stations[[constants.FIELD_STAID, constants.FIELD_STANAME]] #filter and leave only two fields we need to render
    stations[constants.FIELD_STANAME] = stations[constants.FIELD_STANAME].str.strip()
    return stations


def load_station(stationid: str) -> pd.DataFrame:
    """
    Loads the station CSV file by stationid and validates it exists before loading it.
    """
    validators.validate_station_id(stationid)
    station_file_path = os.path.join(os.getcwd(), "data", f"TG_STAID{stationid.zfill(6)}.txt")
    validators.validate_file_existence(station_file_path)

    return _load_and_clean_data(file_path=station_file_path, 
                                rows_to_skip=constants.ROWS_TO_SKIP_STATION, 
                                parse_dates=True)