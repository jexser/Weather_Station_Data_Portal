from errors import BadRequest, NotFound
from typing import Any
import re, datetime, logging, pandas
from pathlib import Path
import constants

def validate_station_id(stationid: str) -> None:
    """
    Validates the station ID format. It should be a string of 1 to 6 digits.
    Args:        
        stationid (str): The station ID to validate.
    Raises:
        BadRequest: If the station ID format is invalid.
    """
    if not constants.PATTERN_STATION_ID.fullmatch(stationid):
        logging.warning(f"Invalid station ID format: {stationid}")
        raise BadRequest("Invalid station ID format. Please provide a valid station ID.")


def validate_file_existence(file_path: Path) -> None:
    """
    Checks if the specified file exists. If it does not exist, raises a NotFound error.
    Args:
        file_path (str): The path to the file to check.
    Raises:
        NotFound: If the file does not exist.
    """
    if not file_path.exists():
        logging.warning(f"File not found at path: {file_path}")
        raise NotFound("Station data not found.")


def validate_date_and_year_args(date_str: str | None, year_str: str | None) -> None:
    """
    Validates that exactly one of date_str or year_str is provided.
    Args:
        date_str (str | None): The date query parameter, or None if not provided.
        year_str (str | None): The year query parameter, or None if not provided.
    Raises:
        BadRequest: If both date_str and year_str are provided.
        BadRequest: If neither date_str nor year_str are provided.
    """
    if (date_str) and (year_str):
        logging.warning("Both 'year' and 'date' query parameters provided: %s, %s", date_str, year_str)
        raise BadRequest("Please provide one query parameter: either 'year' or 'date'")
    if (not date_str) and (not year_str):
        logging.warning("Neither 'year' or 'date' query parameters provided")
        raise BadRequest("Please provide one query parameter: either 'year' or 'date'")


def validate_date_format(date_str: str) -> datetime.datetime:
    """
    Validates the date format. It should be in the format YYYY-MM-DD.
    Args:
        date_str (str): The date string to validate.
    Returns:
        datetime.datetime: The parsed datetime object if the format is valid.
    Raises:
        BadRequest: If the date format is invalid.
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        logging.warning(f"Invalid date format: {date_str}")
        raise BadRequest("Invalid date, please provide a valid calendar date in the format YYYY-MM-DD")


def validate_year_format(year_str: str) -> None:
    """
    Validates the year format. It should be a 4-digit number.
    Args:
        year_str (str): The year string to validate.
    Raises:
        BadRequest: If the year format is invalid.
    """
    if not constants.PATTERN_YEAR.fullmatch(year_str):
        logging.warning(f"Invalid year format: {year_str}")
        raise BadRequest("Invalid year format, please provide a 4-digit year")


def validate_mm_dd_date_format(date_str: str) -> str:
    """
    Validates the date format for insight queries. It should be in the format MM-DD.
    Args:
        date_str (str): The date string to validate.
    Returns:
        str: The original date string if the format is valid.
    Raises:
        BadRequest: If the date format is invalid.
    """
    if not re.fullmatch(r"\d{2}-\d{2}", date_str):
        logging.warning("Invalid MM-DD date format: %s", date_str)
        raise BadRequest("Invalid date, please provide a valid calendar date in the format MM-DD")

    try:
        datetime.datetime.strptime(f"2000-{date_str}", "%Y-%m-%d")
    except ValueError:
        logging.warning("Invalid MM-DD calendar date: %s", date_str)
        raise BadRequest("Invalid date, please provide a valid calendar date in the format MM-DD")

    return date_str


def validate_insight_params(insight_type: str, date_str: str | None) -> None:
    """
    Validates supported insight types and the optional MM-DD date parameter.
    Args:
        insight_type (str): Requested insight type.
        date_str (str | None): Optional MM-DD date for date-dependent insights.
    Raises:
        BadRequest: If the insight type is unsupported or the date format is invalid.
    """
    supported_types = {
        "hottest_year",
        "coldest_year",
        "hottest_day",
        "coldest_day",
        "avg_for_date",
        "temp_variability",
        "missing_data_count",
    }
    date_required_types = {"avg_for_date", "temp_variability"}

    if insight_type not in supported_types:
        logging.warning("Unsupported insight type requested: %s", insight_type)
        raise BadRequest("Invalid insight type.")

    if insight_type in date_required_types and date_str:
        validate_mm_dd_date_format(date_str)


def validate_temperature_data(temperature_series: Any) -> float:
    """
    Validates the temperature data. It checks if the data is empty or cannot be converted to a float.
    Args:
        temperature_series (Any): The result of a pandas .squeeze() call — a scalar when one row matches, a Series when multiple rows match.
    Returns:
        float: The validated temperature value if the data is valid.
    Raises:
        BadRequest: If the temperature data is empty or cannot be converted to a float.
    """
    try:
        temperature = float(temperature_series)
        if pandas.isna(temperature):
            logging.warning("Temperature data is NaN.")
            raise ValueError("Empty data")
        return temperature
    except (ValueError, TypeError):
        logging.warning(f"Invalid temperature data: {temperature_series}")
        raise NotFound("No temperature data found")
    

def validate_page_number(page_str: str | None) -> int:
    """
    Validates the page number. It should be a an integer in the form of a string.
    Args:
        page_str (str | None): The page number as a string.
    Returns:
        int: Validated integer page number
    Raises:
        BadRequest: If page_str is None, not a valid integer, or less than 1.
    """
    if page_str is None:
        raise BadRequest("Please provide a page number")
    
    try:
        page = int(page_str)
    except ValueError:
        raise BadRequest("Page must be integer and >= 1")
    
    if page < 1:
        raise BadRequest("Page must be integer and >= 1")
    
    return page


def validate_station_name(station_name: str) -> None:
    """
    Validates that a station name contains only allowed characters.
    Args:
        staion_name (str): The station name to validate.
    Raises:
        BadRequest: If the name contains characters outside of letters, spaces, dashes, apostrophes, or dots.
    """
    if not constants.PATTERN_STATION_NAME.fullmatch(station_name):
        logging.warning(f"Incorrect station name requested: {station_name}")
        raise BadRequest("Provide correct name; Allowed characters: Letters, space, dash, apostrophe, dot")
