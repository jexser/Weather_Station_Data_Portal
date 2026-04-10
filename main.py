from flask import Flask, render_template, request, jsonify
import pandas as pd
from dataclasses import dataclass
import re
import datetime

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


def load_and_clean_data(
        file_path: str, 
        rows_to_skip: int = 0, 
        parse_dates: bool = False
        ) -> pd.DataFrame:
    """
    Loads a CSV file, skipping a specified number of rows (0 by default)
    Optionally, parses the date column. 
    Removes any leading or trailing whitespace from the column names.
    Returns a cleaned DataFrame ready for analysis or further processing.
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

    return df


@app.route("/")
def home():
    stations = load_and_clean_data("data_small\\stations.txt", rows_to_skip=17, parse_dates=False)
    stations = stations[[Fields.field_STAID, Fields.field_STANAME]]
    return render_template("home.html", data=stations.to_html())


@app.route("/api/v1/station/<stationid>")
def get_station_by(stationid):
    year_str = request.args.get("year")
    date_str = request.args.get("date")
    
    file_path = "data_small\\TG_STAID" + str(stationid).zfill(6) + ".txt"
    df = load_and_clean_data(file_path=file_path, rows_to_skip=20, parse_dates=True)

    if date_str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str): # error handling for invalid date format
            return jsonify({"error": "Invalid date format. Please provide a date in the format YYYY-MM-DD."}), 400
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date. Please provide a valid calendar date in the format YYYY-MM-DD."}), 400
        
        temperature = df.loc[df[Fields.field_DATE] == date_str][Fields.field_TG].squeeze()
        return jsonify({
                    "stationid": stationid,
                    "date": date_str, 
                    "temperature": temperature
                })
    elif year_str:
        if not re.match(r"^\d{4}$", year_str): # error handling for invalid year format
            return jsonify({"error": "Invalid year format. Please provide a 4-digit year."}), 400
        result = df.loc[df[Fields.field_DATE].dt.year == int(year_str)].to_dict(orient="records")
        return jsonify(result)

    return jsonify({"error": "Please provide either a 'year' or 'date' query parameter."}), 400


if __name__ == "__main__":
    app.run(debug=True)