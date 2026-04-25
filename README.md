# Weather Station Data Portal

A Flask-based web application and RESTful API providing access to historical temperature records from ECA&D weather stations stored as flat files.

## Overview

The project has two parts:

1. **Web Portal** — Browse and search stations; visualise temperature trends via charts; explore statistical insights; compare two stations side by side; read API reference docs.
2. **RESTful API** — Query temperature records, statistical insights, and station comparisons. Designed for both the portal UI and external consumers.

## Project Structure

```text
.
├── data/
│   ├── stations.txt            # Station index (97 stations; 17 header lines)
│   └── TG_STAIDXXXXXX.txt      # Per-station daily temperature records (20 header lines)
├── logs/                       # Rotating log output
├── repositories/
│   └── station_repository.py   # File I/O; LRU-cached data loading
├── routes/
│   ├── api.py                  # JSON API endpoints (Blueprint: api_bp)
│   └── ui.py                   # HTML UI routes (Blueprint: ui_bp)
├── services/
│   ├── station_service.py      # Business logic: pagination, search, filtering, insight dispatch
│   └── handlers.py             # Statistical insight functions
├── static/
│   ├── css/components.css      # All styles (navy + lime color scheme)
│   └── scripts/combo-search.js # Station autocomplete widget
├── templates/
│   ├── base.html               # Master layout with nav
│   ├── home.html               # Station browser (paginated table + search)
│   ├── insights.html           # Statistical insights per station
│   ├── charts.html             # Temperature trend charts
│   ├── compare.html            # Side-by-side station comparison
│   ├── api.html                # Static API reference documentation
│   ├── error.html              # 500 error page
│   └── macros.html             # Shared Jinja2 macros (pagination)
├── tests/                      # Pytest test suite
├── app.py                      # App init, logging, blueprint registration, entry point
├── constants.py                # Field names and config constants
├── errors.py                   # APIError hierarchy and JSON serializer
├── models.py                   # Frozen dataclasses for all service/repo return types
├── pytest.toml                 # Pytest configuration
├── validators.py               # Input validation (raises 400/404 on failure)
└── requirements.txt
```

## Architecture

Requests flow through three layers:

```
Route handlers (routes/api.py, routes/ui.py)
  → Service layer (services/station_service.py, services/handlers.py)
    → Repository layer (repositories/station_repository.py)
      → Flat files (data/)
```

Routes are organised as Flask Blueprints (`api_bp`, `ui_bp`) registered in `app.py`. The repository's `_load_and_clean_data()` is LRU-cached by file path, so repeated requests for the same station avoid disk reads. It handles header skipping, whitespace stripping, TG scaling (÷10 → °C), and `-9999` → `null` replacement. All service and repo return types are typed frozen dataclasses in `models.py`.

Dispatcher pattern implemented in `handlers.py` to handle different types of requests.

## Web Pages

| Route | Page |
|---|---|
| `GET /` | Station browser — paginated table with name search |
| `GET /insights` | Statistical insights for a selected station |
| `GET /charts` | Temperature trend charts (yearly average or same date across years) |
| `GET /compare` | Side-by-side daily temperature comparison for two stations |
| `GET /api` | Static API reference documentation |
| `GET /error` | 500 error page |

## API Endpoints

All endpoints return JSON. Base path: `/api/v1`. No authentication required.

### Response envelope

**Success**
```json
{ "data": { ... } | [ ... ], "items": <int> }
```

**Error**
```json
{ "error": { "status_code": 400, "message": "Human-readable description." } }
```

---

### `GET /api/v1/stations`

Paginated list of all stations.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `page` | integer | No | Page number (default: 1). Returns `{"data": []}` beyond last page. |

```json
{
  "data": [{ "STAID": "000001", "STANAME": "VILNIUS" }],
  "items": 97,
  "page": 1,
  "page_size": 20,
  "total_pages": 5,
  "has_next": true
}
```

---

### `GET /api/v1/stations/search`

Case-insensitive partial name match. Returns up to 50 results.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Partial station name. Returns 400 if missing. |

```json
{ "data": [{ "STAID": "000001", "STANAME": "VILNIUS" }], "search_query": "vil", "items": 1 }
```

---

### `GET /api/v1/station/{id}?date=YYYY-MM-DD`

Temperature for a single date. Mutually exclusive with `year`.

```json
{ "data": { "stationid": "000001", "date": "2003-08-12", "temperature": 38.2 }, "items": 1 }
```

---

### `GET /api/v1/station/{id}?year=YYYY`

All daily records for a year. Missing values (`-9999`) returned as `null`.

```json
{
  "data": [
    { "date": "2003-01-01", "temperature": -3.1 },
    { "date": "2003-01-02", "temperature": null }
  ],
  "items": 365
}
```

---

### `GET /api/v1/station/{id}/yearly`

One mean temperature per year across all available data. Years with no valid records are omitted.

```json
{ "data": [{ "year": 1960, "temperature": 6.1 }], "items": 62, "stationid": "000001" }
```

---

### `GET /api/v1/station/{id}/date/{mm_dd}`

Temperature recorded on a specific calendar date (`MM-DD`) across all available years.

```json
{
  "data": [{ "date": "2000-07-15", "temperature": 24.3 }],
  "items": 60,
  "stationid": "000001",
  "mm_dd": "07-15"
}
```

---

### `GET /api/v1/insights/{id}`

Statistical insight for a station. `type` is required; `date` (MM-DD) is required for `avg_for_date` and `temp_variability`.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `type` | string | Yes | Insight type — see table below. |
| `date` | string | Conditional | `MM-DD` format. Required for `avg_for_date` and `temp_variability`. |

| `type` | `date` required | Response `data` keys |
|---|---|---|
| `hottest_year` | no | `year`, `value` |
| `coldest_year` | no | `year`, `value` |
| `hottest_day` | no | `date`, `value` |
| `coldest_day` | no | `date`, `value` |
| `avg_for_date` | yes | `avg_temp` |
| `temp_variability` | yes | `std_dev` |
| `missing_data_count` | no | `missing_count` |

```json
{ "data": { "year": 2003, "value": 12.4 } }
```

---

### `GET /api/v1/compare`

Full-year union of daily temperatures for two stations. Every calendar day in the requested year is present; missing values are `null`.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `stationA_id` | integer | Yes | Station A numeric ID. |
| `stationB_id` | integer | Yes | Station B numeric ID. |
| `year` | integer | Yes | Four-digit year. |

```json
{
  "data": [{ "date": "2003-01-01", "stationA": -3.1, "stationB": -1.8 }],
  "items": 365,
  "stationA_id": "000001",
  "stationB_id": "000002",
  "year": "2003"
}
```

---

### Error codes

| Status | Condition |
|---|---|
| 400 | Invalid/non-numeric station ID, bad date/year format, `date` and `year` both provided, missing required parameter, unsupported insight type |
| 404 | Station file not found, no record for requested date |
| 500 | Unexpected server error |

## Getting Started

### Prerequisites

Python 3.10+

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
Debug=True
```

`Debug=True` enables Flask hot-reload and DEBUG-level logging. Omit or set to `False` for production.

### Running

```bash
python app.py
```

Runs on `http://127.0.0.1:5000`.

### Running Tests

```bash
pytest
```

## Tech Stack

- **Python 3.10+**
- **Flask 3.x** — web framework and routing
- **Pandas 3.x** — data loading and transformation
- **NumPy 2.x** — numerical operations (std dev, aggregation)
- **Jinja2** — HTML templating
- **Chart.js** — client-side temperature trend charts
- **Vanilla JS** — station autocomplete widget (no frontend framework)
- **pytest** — test suite
