import pytest
from errors import BadRequest
from models import (
    DailyTemperatureRecord,
    StationDateAcrossYearsResult,
    StationRecord,
    StationYearlyAveragesResult,
    StationYearlyResult,
    YearlyTemperatureRecord,
)
import services.station_service as station_service


def test_get_stations_index_page_returns_domain_result(monkeypatch):
    stations = [
        StationRecord(station_id="000001", station_name="Vilnius"),
        StationRecord(station_id="000002", station_name="Kaunas"),
    ]

    monkeypatch.setattr(station_service.station_repository, "get_station_index", lambda: stations)
    monkeypatch.setattr(station_service.constants, "INDEX_PAGE_SIZE", 1)

    result = station_service.get_stations_index_page("2")

    assert result.page == 2
    assert result.page_size == 1
    assert result.total_items == 2
    assert result.total_pages == 2
    assert result.has_next is False
    assert result.stations == (stations[1],)


def test_find_stations_by_name_returns_limited_domain_result(monkeypatch):
    search_results = [
        StationRecord(station_id="000001", station_name="Vilnius"),
        StationRecord(station_id="000002", station_name="Vilkaviskis"),
    ]

    monkeypatch.setattr(
        station_service.station_repository,
        "search_stations_by_name",
        lambda query: search_results,
    )
    monkeypatch.setattr(station_service.constants, "SEARCH_RESULTS_LIMIT", 1)

    result = station_service.find_stations_by_name("vil")

    assert result.query == "vil"
    assert result.limit == 1
    assert result.stations == (search_results[0],)


def test_get_station_yearly_averages_returns_result(monkeypatch):
    records = [
        YearlyTemperatureRecord(year=2020, temperature=5.3),
        YearlyTemperatureRecord(year=2021, temperature=6.1),
    ]
    monkeypatch.setattr(
        station_service.station_repository,
        "extract_yearly_averages",
        lambda stationid: records,
    )

    result = station_service.get_station_yearly_averages("1")

    assert isinstance(result, StationYearlyAveragesResult)
    assert result.station_id == "1"
    assert result.records == tuple(records)


def test_get_station_yearly_averages_invalid_id_raises():
    with pytest.raises(BadRequest):
        station_service.get_station_yearly_averages("abc")


def test_get_station_temperature_for_date_returns_result(monkeypatch):
    records = [
        DailyTemperatureRecord(date="2020-02-27", temperature=1.5),
        DailyTemperatureRecord(date="2021-02-27", temperature=2.3),
    ]
    monkeypatch.setattr(
        station_service.station_repository,
        "extract_temperature_series_for_date",
        lambda stationid, mm_dd: records,
    )

    result = station_service.get_station_temperature_for_date("1", "02-27")

    assert isinstance(result, StationDateAcrossYearsResult)
    assert result.station_id == "1"
    assert result.mm_dd == "02-27"
    assert result.records == tuple(records)


def test_get_station_temperature_for_date_invalid_id_raises():
    with pytest.raises(BadRequest):
        station_service.get_station_temperature_for_date("abc", "02-27")


def test_get_station_temperature_for_date_invalid_mm_dd_raises():
    with pytest.raises(BadRequest):
        station_service.get_station_temperature_for_date("1", "2020-02-27")


def test_get_station_data_by_date_or_year_returns_yearly_result(monkeypatch):
    daily_record = DailyTemperatureRecord(date="2020-01-01", temperature=-1.2)

    monkeypatch.setattr(
        station_service.station_repository,
        "extract_temperature_series",
        lambda stationid, year_str: [daily_record],
    )

    result = station_service.get_station_data_by_date_or_year("1", None, "2020")

    assert isinstance(result, StationYearlyResult)
    assert result.station_id == "1"
    assert result.year == "2020"
    assert result.records == (daily_record,)
