from errors import APIError, BadRequest, NotFound
import re, os, datetime, logging, pandas


def validate_station_id(stationid: str) -> APIError | None:
    """
    Validates the station ID format. It should be a string of 1 to 6 digits.
    Args:        
        stationid (str): The station ID to validate.
    Raises:
        BadRequest: If the station ID format is invalid.
    """
    if not re.match(r"^\d{1,6}$", stationid):
        logging.warning(f"Invalid station ID format: {stationid}")
        raise BadRequest("Invalid station ID format. Please provide a valid station ID.")


def validate_file_existence(file_path: str) -> APIError | None:
    """
    Checks if the specified file exists. If it does not exist, raises a NotFound error.
    Args:
        file_path (str): The path to the file to check.
    Raises:
        NotFound: If the file does not exist.
    """
    if not os.path.exists(path=file_path):
        logging.warning(f"File not found at path: {file_path}")
        raise NotFound("Station data not found.")


def validate_date_and_year_args(date_str: str | None, year_str: str | None) -> None:
    """
    Validates the query parameters in the request. It checks that either 'year' or 'date' is provided, but not both.
    Args:     
        args (dict): The dictionary of query parameters from the request.
    Raises:
        BadRequest: If both 'year' and 'date' are provided
    """
    if (date_str) and (year_str):
        logging.warning("Both 'year' and 'date' query parameters provided: %s, %s", date_str, year_str)
        raise BadRequest("Please provide only one query parameter: either 'year' or 'date', not both.")
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
        raise BadRequest("Invalid date. Please provide a valid calendar date in the format YYYY-MM-DD.")


def validate_year_format(year_str: str) -> None:
    """
    Validates the year format. It should be a 4-digit number.
    Args:
        year_str (str): The year string to validate.
    Raises:
        BadRequest: If the year format is invalid.
    """
    if not re.match(r"^\d{4}$", year_str):
        logging.warning(f"Invalid year format: {year_str}")
        raise BadRequest("Invalid year format. Please provide a 4-digit year.")


def validate_temperature_data(temperature_series) -> float | None:
    """
    Validates the temperature data. It checks if the data is empty or cannot be converted to a float.
    Args:
        temperature_series: The temperature data to validate, typically a pandas Series.
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
        raise BadRequest("No temperature data found.")
    

def validate_page_number(page_str: str | None) -> int:
    """
    Validates the page number. It should be a an integer in the form of a string.
    Args:
        page_str (str | None): The page number as a string.
    Returns:
        int: Validated integer page number
    Raises:
        BadRequest: If the page number is not a valid integer.
    """
    if page_str is None:
        raise BadRequest("Please provide a page number")
    
    try:
        page = int(page_str)
    except ValueError:
        raise BadRequest("Page must be integer")
    
    if page < 1:
        raise BadRequest("Page must be >= 1")
    
    return page


def validate_station_name(staion_name: str):
    pattern = "^[A-Za-z\\s'-.]+$"
    if not re.match(pattern=pattern, string=staion_name):
        raise BadRequest("Provide correct name; Allowed characters: Letters, space, dash, apostrophe, dot")