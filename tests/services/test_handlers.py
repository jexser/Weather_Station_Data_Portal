import pandas as pd
import pytest

from errors import BadRequest, NotFound
import services.handlers as handlers


def _build_station_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "DATE": pd.to_datetime(
                [
                    "2020-01-01",
                    "2020-07-11",
                    "2021-01-01",
                    "2021-07-11",
                    "2022-07-11",
                    "2022-12-31",
                ]
            ),
            "TG": [-5.0, 10.0, 5.0, 20.0, pd.NA, -10.0],
        }
    )


def test_get_hottest_year_returns_year(monkeypatch):
    monkeypatch.setattr(handlers.station_repository, "_load_station", lambda stationid: _build_station_df())

    result = handlers._get_hottest_year("1", None)

    assert result == {"data": {"year": 2021}}


def test_get_coldest_year_returns_year(monkeypatch):
    monkeypatch.setattr(handlers.station_repository, "_load_station", lambda stationid: _build_station_df())

    result = handlers._get_coldest_year("1", None)

    assert result == {"data": {"year": 2022}}


def test_get_hottest_day_returns_date_and_temperature(monkeypatch):
    monkeypatch.setattr(handlers.station_repository, "_load_station", lambda stationid: _build_station_df())

    result = handlers._get_hottest_day("1", None)

    assert result == {"data": {"date": "2021-07-11", "TG": 20.0}}


def test_get_coldest_day_returns_date_and_temperature(monkeypatch):
    monkeypatch.setattr(handlers.station_repository, "_load_station", lambda stationid: _build_station_df())

    result = handlers._get_coldest_day("1", None)

    assert result == {"data": {"date": "2022-12-31", "TG": -10.0}}


def test_get_avg_for_date_returns_rounded_average(monkeypatch):
    monkeypatch.setattr(handlers.station_repository, "_load_station", lambda stationid: _build_station_df())

    result = handlers._get_avg_for_date("1", "07-11")

    assert result == {"data": {"avg_temp": 15.0}}


def test_get_avg_for_date_requires_date():
    with pytest.raises(BadRequest) as exc:
        handlers._get_avg_for_date("1", None)

    assert str(exc.value) == "Parameter 'date' (MM-DD) is required for this insight type."


def test_get_avg_for_date_raises_not_found_when_no_matching_rows(monkeypatch):
    monkeypatch.setattr(handlers.station_repository, "_load_station", lambda stationid: _build_station_df())

    with pytest.raises(NotFound) as exc:
        handlers._get_avg_for_date("1", "03-15")

    assert str(exc.value) == "No data for given date"


def test_get_temp_variability_returns_rounded_std_dev(monkeypatch):
    monkeypatch.setattr(handlers.station_repository, "_load_station", lambda stationid: _build_station_df())

    result = handlers._get_temp_variability("1", "01-01")

    assert result == {"data": {"std_dev": 7.1}}


def test_get_temp_variability_requires_date():
    with pytest.raises(BadRequest) as exc:
        handlers._get_temp_variability("1", None)

    assert str(exc.value) == "Parameter 'date' (MM-DD) is required for this insight type."


def test_get_temp_variability_raises_not_found_when_no_matching_rows(monkeypatch):
    monkeypatch.setattr(handlers.station_repository, "_load_station", lambda stationid: _build_station_df())

    with pytest.raises(NotFound) as exc:
        handlers._get_temp_variability("1", "03-15")

    assert str(exc.value) == "No data for given date"


def test_get_missing_data_count_returns_count(monkeypatch):
    monkeypatch.setattr(handlers.station_repository, "_load_station", lambda stationid: _build_station_df())

    result = handlers._get_missing_data_count("1", None)

    assert result == {"data": {"missing_count": 1}}
