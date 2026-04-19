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
