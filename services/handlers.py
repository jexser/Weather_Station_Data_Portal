import constants
import repositories.station_repository as station_repository
from errors import BadRequest, NotFound

_DATE_REQUIRED_MSG = "Parameter 'date' (MM-DD) is required for this insight type."


def _get_hottest_year(stationid: str, date_mm_dd: str | None) -> dict:
    """Returns the year with the highest mean daily temperature for the station."""
    df = station_repository._load_station(stationid=stationid).copy()
    year_avg = df.groupby(df[constants.FIELD_DATE].dt.year)[constants.FIELD_TG].mean()
    max_temp_year = int(year_avg.idxmax())
    avg_temp_for_max_year = round(float(year_avg.loc[max_temp_year]), 1)
    return {"data": {"year": max_temp_year, "value": avg_temp_for_max_year}}


def _get_coldest_year(stationid: str, date_mm_dd: str | None) -> dict:
    """Returns the year with the lowest mean daily temperature for the station."""
    df = station_repository._load_station(stationid=stationid).copy()
    year_avg = df.groupby(df[constants.FIELD_DATE].dt.year)[constants.FIELD_TG].mean()
    min_temp_year = int(year_avg.idxmin())
    avg_temp_for_min_year = round(float(year_avg.loc[min_temp_year]), 1)
    return {"data": {"year": min_temp_year, "value": avg_temp_for_min_year}}


def _get_hottest_day(stationid: str, date_mm_dd: str | None) -> dict:
    """Returns the date and temperature of the single hottest recorded day."""
    df = station_repository._load_station(stationid=stationid).copy()
    row = df.loc[df[constants.FIELD_TG] == df[constants.FIELD_TG].max()].iloc[0]
    return {"data": {"date": row[constants.FIELD_DATE].strftime("%Y-%m-%d"), "value": float(row[constants.FIELD_TG])}}


def _get_coldest_day(stationid: str, date_mm_dd: str | None) -> dict:
    """Returns the date and temperature of the single coldest recorded day."""
    df = station_repository._load_station(stationid=stationid).copy()
    row = df.loc[df[constants.FIELD_TG] == df[constants.FIELD_TG].min()].iloc[0]
    return {"data": {"date": row[constants.FIELD_DATE].strftime("%Y-%m-%d"), "value": float(row[constants.FIELD_TG])}}


def _get_avg_for_date(stationid: str, date_mm_dd: str | None) -> dict:
    """Returns the mean temperature across all years for the given MM-DD, rounded to 1 dp.

    Raises BadRequest if date_mm_dd is not provided, NotFound if no records match.
    """
    if not date_mm_dd:
        raise BadRequest(_DATE_REQUIRED_MSG)
    df = station_repository._load_station(stationid=stationid).copy()
    filtered = df[df[constants.FIELD_DATE].dt.strftime("%m-%d") == date_mm_dd]
    if filtered.empty:
        raise NotFound("No data for given date")
    return {"data": {"avg_temp": round(float(filtered[constants.FIELD_TG].mean()), 1)}}


def _get_temp_variability(stationid: str, date_mm_dd: str | None) -> dict:
    """Returns the standard deviation of temperatures across all years for the given MM-DD, rounded to 1 dp.

    Raises BadRequest if date_mm_dd is not provided, NotFound if no records match.
    """
    if not date_mm_dd:
        raise BadRequest(_DATE_REQUIRED_MSG)
    df = station_repository._load_station(stationid=stationid).copy()
    filtered = df[df[constants.FIELD_DATE].dt.strftime("%m-%d") == date_mm_dd]
    if filtered.empty:
        raise NotFound("No data for given date")
    return {"data": {"std_dev": round(float(filtered[constants.FIELD_TG].std()), 1)}}


def _get_missing_data_count(stationid: str, date_mm_dd: str | None) -> dict:
    """Returns the count of missing (-9999) temperature entries in the station file."""
    df = station_repository._load_station(stationid=stationid).copy()
    return {"data": {"missing_count": int(df[constants.FIELD_TG].isna().sum())}}