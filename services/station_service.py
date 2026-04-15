import errors, validators, constants, repositories.station_repository as station_repo
import pandas as pd


def get_stations_index() -> pd.DataFrame:
    """
    Returns the stations index as a DataFrame with station IDs and names.
    """
    return station_repo.load_station_index()

def get_by_date_or_year(stationid: str, date_str: str | None, year_str: str | None) -> dict | list:
    """
    Returns temperature data for a station filtered by a specific date or year.
    Exactly one of date_str or year_str must be provided.
    For a date query, returns a dict with stationid, date, and temperature.
    For a year query, returns a list of daily records for that year.
    """
    validators.validate_date_and_year_args(date_str, year_str)
    df = station_repo.load_station(stationid)
    result = {}

    if date_str:
        parsed_date = validators.validate_date_format(date_str)
        temperature_series = df.loc[df[constants.FIELD_DATE] == parsed_date][constants.FIELD_TG].squeeze()
        temperature = validators.validate_temperature_data(temperature_series)

        result = {
            "stationid": stationid,
            "date": date_str, 
            "temperature": temperature
        }
    elif year_str:
        validators.validate_year_format(year_str)
        
        result = df.loc[df[constants.FIELD_DATE].dt.year == int(year_str)].to_dict(orient="records")
        #if no data, it will return an empty list, which is appropriate for this case
    else:
        raise errors.BadRequest("Either date or year must be provided")

    return result