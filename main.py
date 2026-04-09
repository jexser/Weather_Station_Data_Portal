from flask import Flask, render_template
import pandas as pd
import numpy as np
from dataclasses import dataclass

app = Flask("__name__")

@dataclass 
class CsvFields():
    field_TG: str = "   TG"
    field_DATE: str = "    DATE"

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/v1/<station>/<date>")
def call_api(stationid: int, date) -> dict:
    file_path = "data_small\\TG_STAID" + str(stationid).zfill(6) + ".txt"
    df = pd.read_csv(file_path, skiprows=20, parse_dates=[CsvFields.field_DATE])
    temperature = df.loc[df[CsvFields.field_DATE] == date, [CsvFields.field_TG]].squeeze() / 10 # type: ignore

    return {
                "stationid": stationid,
                "date": date, 
                "temperature": temperature
            }


if __name__ == "__main__":
    app.run(debug=True)