import pandas as pd

import repositories.station_repository as station_repository


def test_get_station_index_returns_internal_station_records(monkeypatch):
    station_index_df = pd.DataFrame(
        [
            {"STAID": 1, "STANAME": "VILNIUS"},
            {"STAID": 25, "STANAME": "KAUNAS"},
        ]
    )

    monkeypatch.setattr(station_repository, "_load_station_index", lambda: station_index_df)

    result = station_repository.get_station_index()

    assert result[0].station_id == "1"
    assert result[0].station_name == "VILNIUS"
    assert result[1].station_id == "25"


def test_extract_yearly_averages_groups_by_year_and_rounds(monkeypatch):
    df = pd.DataFrame({
        "DATE": pd.to_datetime(["2020-06-01", "2020-06-02", "2021-06-01"]),
        "TG": [10.0, 20.0, 15.0],
    })
    monkeypatch.setattr(station_repository, "_load_station", lambda stationid: df)

    result = station_repository.extract_yearly_averages("1")

    assert len(result) == 2
    assert result[0].year == 2020
    assert result[0].temperature == 15.0  # (10 + 20) / 2
    assert result[1].year == 2021
    assert result[1].temperature == 15.0


def test_extract_yearly_averages_excludes_na_and_empty_years(monkeypatch):
    df = pd.DataFrame({
        "DATE": pd.to_datetime(["2020-06-01", "2021-06-01"]),
        "TG": [pd.NA, 8.0],
    })
    monkeypatch.setattr(station_repository, "_load_station", lambda stationid: df)

    result = station_repository.extract_yearly_averages("1")

    assert len(result) == 1
    assert result[0].year == 2021


def test_extract_temperature_series_for_date_filters_by_month_day(monkeypatch):
    df = pd.DataFrame({
        "DATE": pd.to_datetime(["2020-02-27", "2020-02-28", "2021-02-27"]),
        "TG": [5.0, 10.0, 7.0],
    })
    monkeypatch.setattr(station_repository, "_load_station", lambda stationid: df)

    result = station_repository.extract_temperature_series_for_date("1", "02-27")

    assert len(result) == 2
    dates = [r.date for r in result]
    assert "2020-02-27" in dates
    assert "2021-02-27" in dates
    assert "2020-02-28" not in dates


def test_extract_temperature_series_for_date_excludes_na(monkeypatch):
    df = pd.DataFrame({
        "DATE": pd.to_datetime(["2020-02-27", "2021-02-27"]),
        "TG": [pd.NA, 7.0],
    })
    monkeypatch.setattr(station_repository, "_load_station", lambda stationid: df)

    result = station_repository.extract_temperature_series_for_date("1", "02-27")

    assert len(result) == 1
    assert result[0].date == "2021-02-27"
    assert result[0].temperature == 7.0


def test_search_stations_by_name_returns_internal_station_records(monkeypatch):
    station_index_df = pd.DataFrame(
        [
            {"STAID": 1, "STANAME": "VILNIUS"},
            {"STAID": 25, "STANAME": "KAUNAS"},
        ]
    )

    monkeypatch.setattr(station_repository, "_load_station_index", lambda: station_index_df)

    result = station_repository.search_stations_by_name("vil")

    assert len(result) == 1
    assert result[0].station_id == "1"
    assert result[0].station_name == "VILNIUS"
