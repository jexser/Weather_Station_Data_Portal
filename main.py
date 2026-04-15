import validators
import datetime, os, logging
import pandas as pd
from flask import Flask, render_template, request, jsonify
from dataclasses import dataclass
from functools import lru_cache
from errors import APIError, BadRequest, NotFound, InternalServerError
from logging.handlers import RotatingFileHandler
from typing import Final
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file
DEBUG: Final[bool] = str(os.getenv("Debug")).lower() == "true"
LOG_FILE_LOCATION: Final[str] = os.path.join("logs", "app_logs.log")

# Logs
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
handler = RotatingFileHandler(
    LOG_FILE_LOCATION,
    maxBytes=1_048_576,  # 1 MiB
    backupCount=3
)
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[handler, logging.StreamHandler()]
)
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = Flask(__name__)

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
    index_file_path = os.path.join("data", "stations.txt")
    if not os.path.exists(path=index_file_path):
        logging.critical(f"Stations index file not found at path: {index_file_path}")
        return jsonify_error(InternalServerError("Stations index data not found."))
    stations = load_and_clean_data(index_file_path, rows_to_skip=17, parse_dates=False)
    stations = stations[[Fields.field_STAID, Fields.field_STANAME]]
    return render_template("home.html", data=stations.to_dict(orient="records"))


@app.route("/api/v1/station/<stationid>")
def get_station_by(stationid):
    year_str = request.args.get("year")
    date_str = request.args.get("date")
    
    try:
        validators.validate_station_id(stationid)
        station_file_path = os.path.join("data", f"TG_STAID{str(stationid).zfill(6)}.txt")
        validators.validate_file_existence(station_file_path)
        validators.validate_request_args(request.args)
    except APIError as error:
        return jsonify_error(error)

    df = load_and_clean_data(file_path=station_file_path, rows_to_skip=20, parse_dates=True)
    
    try:
        if date_str:
            validators.validate_date_format(date_str)
            parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            temperature_series = df.loc[df[Fields.field_DATE] == parsed_date][Fields.field_TG].squeeze()
            temperature = validators.validate_temperature_data(temperature_series)

            return jsonify({
                "stationid": stationid,
                "date": date_str, 
                "temperature": temperature
            })
        if year_str:
            validators.validate_year_format(year_str)
            result = df.loc[df[Fields.field_DATE].dt.year == int(year_str)].to_dict(orient="records")
            return jsonify(result) #if no data, it will return an empty list, which is appropriate for this case
        
        logging.warning("No valid query parameters provided: %s", request.args)
        raise BadRequest("Please provide a query parameter: either 'year' or 'date'.")
    except APIError as error:
        return jsonify_error(error)


@lru_cache(maxsize=128) # Cache results to improve performance for repeated requests
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
        df[Fields.field_TG] = df[Fields.field_TG].replace(-9999, pd.NA) # Replace -9999 with NaN for better handling of missing data
        df[Fields.field_TG] = df[Fields.field_TG] / 10 # Convert temperature from tenths of degrees to degrees Celsius
    if parse_dates:
        df[Fields.field_DATE] = pd.to_datetime(df[Fields.field_DATE], format="%Y%m%d", errors='coerce') # type: ignore
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

if __name__ == "__main__":
    app.run(debug=True if DEBUG else False)