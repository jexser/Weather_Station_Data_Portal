from flask import Flask, render_template, request, jsonify
import pandas as pd
from dataclasses import dataclass
import re
import datetime
import os
from functools import lru_cache
from errors import APIError, BadRequest, NotFound, InternalServerError

app = Flask("__name__")

@dataclass 
class Fields():
    """
    Data class to hold the field names for the temperature data CSV.
    """
    field_TG: str = "TG"
    field_DATE: str = "DATE"
    field_STAID: str = "STAID"
    field_STANAME: str = "STANAME"


@app.route("/")
def home():
    path = os.path.join("data_small", "stations.txt")
    if not os.path.exists(path=path): # Check if the file exists, will raise an error if it doesn't
        return jsonify_error(InternalServerError("Stations index data not found."))
    stations = load_and_clean_data(path, rows_to_skip=17, parse_dates=False)
    stations = stations[[Fields.field_STAID, Fields.field_STANAME]]
    return render_template("home.html", data=stations.to_html())


@app.route("/api/v1/station/<stationid>")
def get_station_by(stationid):
    year_str = request.args.get("year")
    date_str = request.args.get("date")
    
    try:
        validate_station_id(stationid)
        station_file_path = os.path.join("data_small", f"TG_STAID{str(stationid).zfill(6)}.txt")
        validate_file_existence(station_file_path)
        validate_request_args(request.args)
    except APIError as error:
        return jsonify_error(error)

    df = load_and_clean_data(file_path=station_file_path, rows_to_skip=20, parse_dates=True)
    
    try:
        if date_str:
            validate_date_format(date_str)
            parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            temperature_series = df.loc[df[Fields.field_DATE] == parsed_date][Fields.field_TG].squeeze()
            temperature = validate_temperature_data(temperature_series)

            return jsonify({
                "stationid": stationid,
                "date": date_str, 
                "temperature": temperature
            })
        elif year_str:
            validate_year_format(year_str)
            result = df.loc[df[Fields.field_DATE].dt.year == int(year_str)].to_dict(orient="records")
            return jsonify(result) #if no data, it will return an empty list, which is appropriate for this case
        else:
            raise BadRequest("Please provide a query parameter: either 'year' or 'date'.")
    except APIError as error:
        return jsonify_error(error)


@lru_cache(maxsize=32) # Cache results to improve performance for repeated requests
def load_and_clean_data(
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
    if Fields.field_TG in df.columns:
        df[Fields.field_TG] = df[Fields.field_TG] / 10 # Convert temperature from tenths of degrees to degrees Celsius
    if parse_dates:
        df[Fields.field_DATE] = pd.to_datetime(df[Fields.field_DATE], format="%Y%m%d", errors='coerce') # type: ignore
    # TODO: need filtering and validation for cases where TG = -9999 (missing data)

    return df


def jsonify_error(error: APIError):
    """
    Helper function to create a JSON response for errors.
    Args:
        error (APIError): The error object containing the message and status code.
    Returns:
        A JSON response with the error message and appropriate HTTP status code.
    """

    response = jsonify({
        "error": {
            "status_code": error.status_code,
            "message": error.message
        }
    })
    response.status_code = error.status_code
    return response


def validate_station_id(stationid: str) -> APIError | None:
    """
    Validates the station ID format. It should be a string of 1 to 6 digits.
    Args:        
        stationid (str): The station ID to validate.
    Raises:
        BadRequest: If the station ID format is invalid.
    """
    if not re.match(r"^\d{1,6}$", stationid):
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
        raise NotFound("Station data not found.")


def validate_request_args(args: dict) -> APIError | None:
    """
    Validates the query parameters in the request. It checks that either 'year' or 'date' is provided, but not both.
    Args:     
        args (dict): The dictionary of query parameters from the request.
    Raises:
        BadRequest: If both 'year' and 'date' are provided, or if neither is provided.
    """
    if ("year" in args) and ("date" in args):
        raise BadRequest("Please provide only one query parameter: either 'year' or 'date', not both.")


def validate_date_format(date_str: str) -> APIError | None:
    """
    Validates the date format. It should be in the format YYYY-MM-DD.
    Args:
        date_str (str): The date string to validate.
    Raises:
        BadRequest: If the date format is invalid.
    """
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise BadRequest("Invalid date. Please provide a valid calendar date in the format YYYY-MM-DD.")


def validate_year_format(year_str: str) -> APIError | None:
    """
    Validates the year format. It should be a 4-digit number.
    Args:
        year_str (str): The year string to validate.
    Raises:
        BadRequest: If the year format is invalid.
    """
    if not re.match(r"^\d{4}$", year_str):
        raise BadRequest("Invalid year format. Please provide a 4-digit year.")


def validate_temperature_data(temperature_series) -> APIError | float | None:
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
        if pd.isna(temperature):
            raise ValueError("Empty data")
        return temperature
    except (ValueError, TypeError):
        raise BadRequest("No temperature data found.")


if __name__ == "__main__":
    app.run(debug=True)