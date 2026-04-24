import pytest
from errors import NotFound
from models import (
    DailyTemperatureRecord,
    StationDateAcrossYearsResult,
    StationYearlyAveragesResult,
    YearlyTemperatureRecord,
)
import routes.api as api_module
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


# ── /yearly ────────────────────────────────────────────────────────────────────

def test_yearly_returns_200_with_correct_shape(client, monkeypatch):
    records = (
        YearlyTemperatureRecord(year=2019, temperature=7.2),
        YearlyTemperatureRecord(year=2020, temperature=8.1),
    )
    monkeypatch.setattr(
        api_module.station_service,
        "get_station_yearly_averages",
        lambda stationid: StationYearlyAveragesResult(station_id=stationid, records=records),
    )

    resp = client.get("/api/v1/station/1/yearly")
    body = resp.get_json()

    assert resp.status_code == 200
    assert body["stationid"] == "1"
    assert body["items"] == 2
    assert body["data"][0] == {"year": 2019, "temperature": 7.2}
    assert body["data"][1] == {"year": 2020, "temperature": 8.1}


def test_yearly_invalid_station_id_returns_400(client):
    resp = client.get("/api/v1/station/abc/yearly")
    body = resp.get_json()

    assert resp.status_code == 400
    assert "error" in body


def test_yearly_nonexistent_station_returns_404(client, monkeypatch):
    monkeypatch.setattr(
        api_module.station_service,
        "get_station_yearly_averages",
        lambda stationid: (_ for _ in ()).throw(NotFound("Station data not found.")),
    )

    resp = client.get("/api/v1/station/999999/yearly")

    assert resp.status_code == 404


def test_yearly_empty_dataset_returns_200_with_empty_list(client, monkeypatch):
    monkeypatch.setattr(
        api_module.station_service,
        "get_station_yearly_averages",
        lambda stationid: StationYearlyAveragesResult(station_id=stationid, records=()),
    )

    resp = client.get("/api/v1/station/1/yearly")
    body = resp.get_json()

    assert resp.status_code == 200
    assert body["data"] == []
    assert body["items"] == 0


# ── /date/<mm_dd> ──────────────────────────────────────────────────────────────

def test_date_across_years_returns_200_with_correct_shape(client, monkeypatch):
    records = (
        DailyTemperatureRecord(date="2019-07-15", temperature=22.3),
        DailyTemperatureRecord(date="2020-07-15", temperature=19.8),
    )
    monkeypatch.setattr(
        api_module.station_service,
        "get_station_temperature_for_date",
        lambda stationid, mm_dd: StationDateAcrossYearsResult(
            station_id=stationid, mm_dd=mm_dd, records=records
        ),
    )

    resp = client.get("/api/v1/station/1/date/07-15")
    body = resp.get_json()

    assert resp.status_code == 200
    assert body["stationid"] == "1"
    assert body["mm_dd"] == "07-15"
    assert body["items"] == 2
    assert body["data"][0] == {"date": "2019-07-15", "temperature": 22.3}
    assert body["data"][1] == {"date": "2020-07-15", "temperature": 19.8}


def test_date_across_years_invalid_station_id_returns_400(client):
    resp = client.get("/api/v1/station/abc/date/07-15")
    body = resp.get_json()

    assert resp.status_code == 400
    assert "error" in body


def test_date_across_years_invalid_mm_dd_returns_400(client):
    resp = client.get("/api/v1/station/1/date/2020-07-15")
    body = resp.get_json()

    assert resp.status_code == 400
    assert "error" in body


def test_date_across_years_nonexistent_station_returns_404(client, monkeypatch):
    monkeypatch.setattr(
        api_module.station_service,
        "get_station_temperature_for_date",
        lambda stationid, mm_dd: (_ for _ in ()).throw(NotFound("Station data not found.")),
    )

    resp = client.get("/api/v1/station/999999/date/07-15")

    assert resp.status_code == 404


def test_date_across_years_no_records_returns_200_with_empty_list(client, monkeypatch):
    monkeypatch.setattr(
        api_module.station_service,
        "get_station_temperature_for_date",
        lambda stationid, mm_dd: StationDateAcrossYearsResult(
            station_id=stationid, mm_dd=mm_dd, records=()
        ),
    )

    resp = client.get("/api/v1/station/1/date/02-29")
    body = resp.get_json()

    assert resp.status_code == 200
    assert body["data"] == []
    assert body["items"] == 0
