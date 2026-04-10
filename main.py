from flask import Flask, render_template
import pandas as pd
from dataclasses import dataclass

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


def load_and_clean_data(file_path: str, rows_to_skip: int = 0, parse_dates: bool = False) -> pd.DataFrame:
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

    if parse_dates:
        df[Fields.field_DATE] = pd.to_datetime(df[Fields.field_DATE], format="%Y%m%d", errors='coerce') # type: ignore

    return df


@app.route("/")
def home():
    stations = load_and_clean_data("data_small\\stations.txt", rows_to_skip=17, parse_dates=False)
    stations = stations[[Fields.field_STAID, Fields.field_STANAME]]
    return render_template("home.html", data=stations.to_html())


@app.route("/api/v1/<stationid>/<date>")
def call_api(stationid, date):
    file_path = "data_small\\TG_STAID" + str(stationid).zfill(6) + ".txt"
    df = load_and_clean_data(file_path=file_path, rows_to_skip=20, parse_dates=True)
    temperature = df.loc[df[Fields.field_DATE] == date][Fields.field_TG].squeeze() / 10 # type: ignore

    return {
                "stationid": stationid,
                "date": date, 
                "temperature": temperature
            }


if __name__ == "__main__":
    app.run(debug=True)