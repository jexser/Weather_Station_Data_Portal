import validators
import repositories.station_repository as station_repo
import datetime, os, logging
from flask import Flask, render_template, request, jsonify
from errors import APIError, BadRequest, NotFound, InternalServerError, jsonify_error
from logging.handlers import RotatingFileHandler
from typing import Final
from dotenv import load_dotenv

load_dotenv()
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


@app.route("/")
def home():
    try:
        stations = station_repo.load_station_index()
        return render_template("home.html", data=stations.to_dict(orient="records"))
    except APIError as error:
        logging.warning("Error while loading index file")
        return jsonify_error(error) #TODO: return error page


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

    df = station_repo._load_and_clean_data(file_path=station_file_path, rows_to_skip=20, parse_dates=True)
    
    try:
        if date_str:
            validators.validate_date_format(date_str)
            parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            temperature_series = df.loc[df[station_repo.Fields.field_DATE] == parsed_date][station_repo.Fields.field_TG].squeeze()
            temperature = validators.validate_temperature_data(temperature_series)

            return jsonify({
                "stationid": stationid,
                "date": date_str, 
                "temperature": temperature
            })
        if year_str:
            validators.validate_year_format(year_str)
            result = df.loc[df[station_repo.Fields.field_DATE].dt.year == int(year_str)].to_dict(orient="records")
            return jsonify(result) #if no data, it will return an empty list, which is appropriate for this case
        
        logging.warning("No valid query parameters provided: %s", request.args)
        raise BadRequest("Please provide a query parameter: either 'year' or 'date'.")
    except APIError as error:
        return jsonify_error(error)


if __name__ == "__main__":
    app.run(debug=True if DEBUG else False)