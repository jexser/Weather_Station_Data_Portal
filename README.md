# Weather Station Data Portal

A Flask-based web application and RESTful API providing access to historical temperature records from ECA&D weather stations stored as flat files.

## Overview

The project has two parts:

1. **Web Portal** — Browse and search weather stations; view paginated station lists; explore statistical insights per station.
2. **RESTful API** — Query temperature records and statistical insights by station, date, or year. Designed for use by both the portal UI and external consumers.

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
│   └── handlers.py             # Statistical insight functions (hottest/coldest, avg, variability)
├── static/
│   ├── css/components.css      # All styles (navy + lime color scheme)
│   └── scripts/combo-search.js # Station autocomplete for insights page
├── templates/
│   ├── base.html               # Master layout
│   ├── home.html               # Station browser UI
│   ├── insights.html           # Statistical insights UI
│   ├── error.html              # 500 error page
│   └── macros.html             # Shared Jinja2 macros (pagination)
├── app.py                      # App init, logging, blueprint registration, entry point
├── constants.py                # Field names and config constants
├── errors.py                   # APIError hierarchy and JSON serializer
├── models.py                   # Frozen dataclasses for all service/repo return types
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

Routes are organised as Flask Blueprints (`api_bp`, `ui_bp`) and registered in `app.py`. The repository's `_load_and_clean_data()` is LRU-cached by file path, so repeated requests for the same station avoid redundant disk reads. It handles header skipping, whitespace stripping, TG scaling (÷10 → °C), and `-9999` → `null` replacement. All service and repo return types are typed frozen dataclasses defined in `models.py`.

### Architecture Decisions

- Layered architecture: routes → services → repositories
- Pandas used only in repository layer
- Caching per station for performance
- Dispatcher pattern for insights endpoint

## API Endpoints

### Station listing

```
GET /api/v1/stations?page=X
```

Returns a paginated list of stations (500 per page in production; page defaults to 1).

```json
{
  "data": [{ "STAID": 1, "STANAME": "VAEXJOE" }],
  "items": 97,
  "page": 1,
  "page_size": 500,
  "total_pages": 1,
  "has_next": false
}
```

### Station search

```
GET /api/v1/stations/search?name=<query>
```

Case-insensitive partial match on station name. Returns up to 50 results in production.

```json
{
  "data": [{ "STAID": 1, "STANAME": "Vaexjoe" }],
  "search_query": "vae",
  "items": 1
}
```

### Temperature by date

```
GET /api/v1/station/<stationid>?date=YYYY-MM-DD
```

```json
{
  "data": { "stationid": "000001", "date": "2023-05-20", "temperature": 15.2 },
  "items": 1
}
```

### Temperature by year

```
GET /api/v1/station/<stationid>?year=YYYY
```

Returns all daily records for that year. Returns `{"data": [], "items": 0}` if the station exists but has no data for that year.

### Statistical insights

```
GET /api/v1/insights/<stationid>?type=<type>[&date=MM-DD]
```

Returns a statistical insight for the station. `type` is required; `date` (MM-DD) is required for `avg_for_date` and `temp_variability`.

| type | date required | Response `data` keys |
|---|---|---|
| `hottest_year` | no | `year`, `value` |
| `coldest_year` | no | `year`, `value` |
| `hottest_day` | no | `date`, `value` |
| `coldest_day` | no | `date`, `value` |
| `avg_for_date` | yes | `avg_temp` |
| `temp_variability` | yes | `std_dev` |
| `missing_data_count` | no | `missing_count` |

```json
{ "data": { "year": 2019, "value": 12.4 } }
```

### Error responses

All errors use a consistent envelope:

```json
{ "error": { "status_code": 400, "message": "..." } }
```

| Status | Condition |
|---|---|
| 400 | Invalid station ID, bad date/year format, both `date` and `year` provided, missing required param, unsupported insight type |
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

## Tech Stack

- **Python 3.10+**
- **Flask 3.x** — web framework and routing
- **Pandas 3.x** — data loading and transformation
- **Jinja2** — HTML templating
- **Vanilla JS** — station autocomplete (no frontend framework)
