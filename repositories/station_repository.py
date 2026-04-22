import datetime
import logging
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

import constants
import validators
from errors import InternalServerError, NotFound
from models import DailyTemperatureRecord, StationRecord


@lru_cache(maxsize=128)
def _load_and_clean_data(
    file_path: Path,
    rows_to_skip: int = 0,
    parse_dates: bool = False,
) -> pd.DataFrame:
    """
    Loads an ECA&D-format CSV file and applies standard cleaning steps.
    Column name whitespace is stripped. If a TG column is present, -9999 sentinels
    are replaced with pd.NA and values are divided by 10 to convert from tenths of
    degrees Celsius to degrees Celsius. Dates are optionally parsed to datetime.
    """
    df = pd.read_csv(file_path, skiprows=rows_to_skip)
    df.columns = df.columns.str.strip()
    if constants.FIELD_TG in df.columns:
        df[constants.FIELD_TG] = df[constants.FIELD_TG].replace(-9999, pd.NA)
        df[constants.FIELD_TG] = df[constants.FIELD_TG] / 10
    if parse_dates:
        df[constants.FIELD_DATE] = pd.to_datetime(
            df[constants.FIELD_DATE],
            format="%Y%m%d",
            errors="coerce",
        )
    return df


def _load_station_index() -> pd.DataFrame:
    """
    Loads the stations index file and returns a cleaned DataFrame with station IDs and names.
    """
    index_file_path = constants.DATA_DIR / "stations.txt"
    if not os.path.exists(path=index_file_path):
        logging.critical("Stations index file not found at path: %s", index_file_path)
        raise InternalServerError("Stations index data not found.")

    stations = _load_and_clean_data(
        index_file_path,
        rows_to_skip=constants.ROWS_TO_SKIP_INDEX,
        parse_dates=False,
    )
    stations = stations[[constants.FIELD_STAID, constants.FIELD_STANAME]]
    stations[constants.FIELD_STANAME] = stations[constants.FIELD_STANAME].str.strip()
    return stations


def _to_station_record(row: pd.Series) -> StationRecord:
    return StationRecord(
        station_id=str(row[constants.FIELD_STAID]),
        station_name=str(row[constants.FIELD_STANAME]),
    )


def get_station_index() -> list[StationRecord]:
    """
    Returns the full station index as internal station records.
    """
    index_df = _load_station_index()
    return [_to_station_record(row) for _, row in index_df.iterrows()]


def _load_station(stationid: str) -> pd.DataFrame:
    """
    Loads a station's temperature data file and returns a cleaned DataFrame.
    """
    validators.validate_station_id(stationid)
    station_file_path = constants.DATA_DIR / f"TG_STAID{stationid.zfill(6)}.txt"
    validators.validate_file_existence(station_file_path)

    return _load_and_clean_data(
        file_path=station_file_path,
        rows_to_skip=constants.ROWS_TO_SKIP_STATION,
        parse_dates=True,
    )


def extract_temperature(stationid: str, date: datetime.datetime) -> float:
    """
    Returns the temperature for a station on a specific date.
    """
    df = _load_station(stationid)
    temperature_series = df.loc[df[constants.FIELD_DATE] == date][constants.FIELD_TG].squeeze()
    return validators.validate_temperature_data(temperature_series)


def extract_temperature_series(stationid: str, year_str: str) -> list[DailyTemperatureRecord]:
    """
    Returns all daily records for a station in a given year.
    """
    df = _load_station(stationid)
    yearly_df = df.loc[df[constants.FIELD_DATE].dt.year == int(year_str)]
    return [
        DailyTemperatureRecord(
            date=row[constants.FIELD_DATE].strftime("%Y-%m-%d"),
            temperature=None if pd.isna(row[constants.FIELD_TG]) else float(row[constants.FIELD_TG]),
        )
        for _, row in yearly_df.iterrows()
    ]


def search_stations_by_name(query: str) -> list[StationRecord]:
    """
    Searches the station index for stations whose names contain the given query string.
    """
    df = _load_station_index()
    search_results = df.loc[
        df[constants.FIELD_STANAME].str.contains(query, case=False, na=False, regex=False)
    ]
    return [_to_station_record(row) for _, row in search_results.iterrows()]


def find_hottest_year(stationid: str) -> int:
    """Returns the year with the highest mean daily temperature, excluding -9999 sentinels."""
    df = _load_station(stationid=stationid).copy()
    year_avg = df.groupby(df[constants.FIELD_DATE].dt.year)[constants.FIELD_TG].mean()
    return int(year_avg.idxmax())


def find_coldest_year(stationid: str) -> int:
    """Returns the year with the lowest mean daily temperature, excluding -9999 sentinels."""
    df = _load_station(stationid=stationid).copy()
    year_avg = df.groupby(df[constants.FIELD_DATE].dt.year)[constants.FIELD_TG].mean()
    return int(year_avg.idxmin())


def find_hottest_day(stationid: str) -> DailyTemperatureRecord:
    """Returns the date and temperature of the single hottest recorded day."""
    df = _load_station(stationid=stationid).copy()
    row = df.loc[df[constants.FIELD_TG] == df[constants.FIELD_TG].max()].iloc[0]
    return DailyTemperatureRecord(
        date=row[constants.FIELD_DATE].strftime("%Y-%m-%d"),
        temperature=float(row[constants.FIELD_TG]),
    )


def find_coldest_day(stationid: str) -> DailyTemperatureRecord:
    """Returns the date and temperature of the single coldest recorded day."""
    df = _load_station(stationid=stationid).copy()
    row = df.loc[df[constants.FIELD_TG] == df[constants.FIELD_TG].min()].iloc[0]
    return DailyTemperatureRecord(
        date=row[constants.FIELD_DATE].strftime("%Y-%m-%d"),
        temperature=float(row[constants.FIELD_TG]),
    )


def find_avg_for_date(stationid: str, date_mm_dd: str) -> float:
    """Returns the mean temperature across all years for the given MM-DD, rounded to 1 dp."""
    df = _load_station(stationid=stationid).copy()
    filtered = df[df[constants.FIELD_DATE].dt.strftime("%m-%d") == date_mm_dd]
    if filtered.empty:
        raise NotFound("No data for given date")
    return round(float(filtered[constants.FIELD_TG].mean()), 1)


def find_std_for_date(stationid: str, date_mm_dd: str) -> float:
    """Returns the standard deviation of temperatures across all years for the given MM-DD, rounded to 1 dp."""
    df = _load_station(stationid=stationid).copy()
    filtered = df[df[constants.FIELD_DATE].dt.strftime("%m-%d") == date_mm_dd]
    if filtered.empty:
        raise NotFound("No data for given date")
    return round(float(filtered[constants.FIELD_TG].std()), 1)


def find_missing_data_count(stationid: str) -> int:
    """Returns the count of -9999 sentinel entries (stored as NA) in the station file."""
    df = _load_station(stationid=stationid).copy()
    return int(df[constants.FIELD_TG].isna().sum())