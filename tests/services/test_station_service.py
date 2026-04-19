from models import DailyTemperatureRecord, StationRecord
import services.station_service as station_service


def test_get_stations_index_page_returns_domain_result(monkeypatch):
    stations = [
        StationRecord(station_id="000001", station_name="Vilnius"),
        StationRecord(station_id="000002", station_name="Kaunas"),
    ]

    monkeypatch.setattr(station_service.station_repo, "get_station_index", lambda: stations)
    monkeypatch.setattr(station_service.constants, "INDEX_PAGE_SIZE", 1)

    result = station_service.get_stations_index_page("2")

    assert result.page == 2
    assert result.page_size == 1
    assert result.total_items == 2
    assert result.total_pages == 2
    assert result.has_next is False
    assert result.stations == [stations[1]]


def test_find_stations_by_name_returns_limited_domain_result(monkeypatch):
    search_results = [
        StationRecord(station_id="000001", station_name="Vilnius"),
        StationRecord(station_id="000002", station_name="Vilkaviskis"),
    ]

    monkeypatch.setattr(
        station_service.station_repo,
        "search_stations_by_name",
        lambda query: search_results,
    )
    monkeypatch.setattr(station_service.constants, "MAX_SEARCH_RESULTS", 1)

    result = station_service.find_stations_by_name("vil")

    assert result.query == "vil"
    assert result.limit == 1
    assert result.stations == [search_results[0]]


def test_get_station_data_by_date_or_year_returns_domain_record_list(monkeypatch):
    yearly_records = [DailyTemperatureRecord(date="2020-01-01", temperature=-1.2)]

    monkeypatch.setattr(
        station_service.station_repo,
        "extract_temperature_series",
        lambda stationid, year_str: yearly_records,
    )

    result = station_service.get_station_data_by_date_or_year("1", None, "2020")

    assert result == yearly_records
