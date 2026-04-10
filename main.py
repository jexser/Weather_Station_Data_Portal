from flask import Flask, render_template
import pandas as pd
from dataclasses import dataclass

app = Flask("__name__")

@dataclass 
class Fields():
    field_TG: str = "   TG"
    field_DATE: str = "    DATE"
    field_STAID: str = "STAID"
    field_STANAME: str = "STANAME                                 "


@app.route("/")
def home():
    stations = pd.read_csv("data_small\\stations.txt", skiprows=17)
    stations = stations[[Fields.field_STAID, Fields.field_STANAME]]
    return render_template("home.html", data=stations.to_html())


@app.route("/api/v1/<stationid>/<date>")
def call_api(stationid, date):
    file_path = "data_small\\TG_STAID" + str(stationid).zfill(6) + ".txt"
    df = pd.read_csv(file_path, skiprows=20, parse_dates=[Fields.field_DATE])
    temperature = df.loc[df[Fields.field_DATE] == date][Fields.field_TG].squeeze() / 10 # type: ignore

    return {
                "stationid": stationid,
                "date": date, 
                "temperature": temperature
            }


if __name__ == "__main__":
    app.run(debug=True)