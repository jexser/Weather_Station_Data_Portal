# Weather Station Data Portal

A Flask-based web application and RESTful API providing access to historical temperature records from ECA&D weather stations stored as flat files.

## Overview

The project has two parts:

1. **Web Portal** — Browse and search weather stations; view paginated station lists.
2. **RESTful API** — Query temperature records by station, date, or year. Designed for use by both the portal UI and external consumers.

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
│   └── ui.py                   # HTML UI route (Blueprint: ui_bp)
├── services/
│   └── station_service.py      # Business logic: pagination, search, filtering
├── templates/
│   ├── home.html               # Station browser UI
│   └── macros.html             # Shared Jinja2 macros (pagination)
├── app.py                      # App init, logging, blueprint registration, entry point
├── constants.py                # Field names and config constants
├── errors.py                   # APIError hierarchy and JSON serializer
├── validators.py               # Input validation (raises 400/404 on failure)
└── requirements.txt
```

## Architecture

Requests flow through three layers:

```
Route handlers (routes/api.py, routes/ui.py)
  → Service layer (services/station_service.py)
    → Repository layer (repositories/station_repository.py)
      → Flat files (data/)
```

Routes are organised as Flask Blueprints (`api_bp`, `ui_bp`) and registered in `app.py`. The repository's `_load_and_clean_data()` is LRU-cached by file path, so repeated requests for the same station avoid redundant disk reads. It handles header skipping, whitespace stripping, TG scaling (÷10 → °C), and `-9999` → `null` replacement.

## API Endpoints

### Station listing

```
GET /api/v1/stations?page=X
```

Returns a paginated list of stations (500 per page; page defaults to 1).

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

Case-insensitive partial match on station name. Returns up to 50 results.

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

### Error responses

All errors use a consistent envelope:

```json
{ "error": { "status_code": 400, "message": "..." } }
```

| Status | Condition |
|---|---|
| 400 | Invalid station ID, bad date/year format, both `date` and `year` provided, missing required param |
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
