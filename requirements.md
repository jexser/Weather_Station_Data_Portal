# Weather API Project – Requirements v2.1

## 1. General Description

A Flask-based web application and RESTful API designed to provide access to historical temperature records from various weather stations stored in a distributed flat-file system.

The system consists of three main parts:

---

## 1.1 Web Portal

A lightweight web interface for browsing, querying, and visualizing weather data.

### 1.1.1 Home Page (`/`, `/home`)
- Displays a table of available weather stations (ID + name)
- Provides navigation to other pages

**Mockup:**

```
+--------------------------------------------------+
| Weather Data Portal                              |
+--------------------------------------------------+
| [Home] [Charts] [Insights] [Compare] [API Docs]   |
+--------------------------------------------------+
| Stations                                         |
| ------------------------------------------------|
| ID     | Name                                   |
| 000001 | Vilnius                                |
| 000002 | Kaunas                                 |
| ...                                              |
+--------------------------------------------------+
```

---

### 1.1.2 API Documentation (`/api`)
- Lists endpoints with examples

**Mockup:**

```
GET /api/v1/station/{id}?date=YYYY-MM-DD
GET /api/v1/station/{id}?year=YYYY
GET /api/v1/insights/{id}?type=...
```

---

### 1.1.3 Charts Page (`/charts`)
User inputs:
- Station dropdown
- Chart type dropdown
- Optional date input

Supported charts:
- Yearly Trend (line)
- Same Date Across Years (scatter)
- Rolling Average (optional)

**Mockup:**

```
Station: [Vilnius ▼]
Chart:   [Yearly Trend ▼]
Date:    [YYYY-MM-DD]

[ Load Chart ]

-------------------------------
|        (Chart Area)         |
-------------------------------
```

---

### 1.1.4 Insights Page (`/insights`)
Displays computed statistics.

**Mockup:**

```
Station: [Vilnius ▼]

[ Load Insights ]

Hottest Year: 2019
Coldest Year: 1963
Avg Temp (July 11): 18.4°C
Temp Variability: ±6.2°C
Missing Records: 12
```

---

### 1.1.5 Compare Page (`/compare`)
Compare two stations.

**Mockup:**

```
Station A: [Vilnius ▼]
Station B: [London ▼]
Year:      [2020]

[ Compare ]

Date       | Vilnius | London
-----------|---------|--------
2020-01-01 | -2.1    | 3.2
...
```

---

### 1.1.6 Error Page (`/error`)
Displays message for internal errors.

---

## 1.2 RESTful API

### 1.2.1 Core Endpoint

GET /api/v1/station/{stationid}

Query params:
- date=YYYY-MM-DD
- year=YYYY

---

### 1.2.2 Insights Endpoint

GET /api/v1/insights/{stationid}

Examples:
- type=hottest_year
- type=coldest_year
- type=avg_for_date&date=YYYY-MM-DD

---

### 1.2.3 Response Format

Success:
```
{
  "data": ...
}
```

Error:
```
{
  "error": {
    "status_code": 400,
    "message": "Description"
  }
}
```

---

## 1.3 Data Storage

- `/data` folder
- stations.txt (CSV, skip first 17 lines)
- TG_STAIDXXXXXX.txt (CSV, skip first 20 lines)

Fields:
- TG (0.1°C)
- DATE
- STAID
- STANAME

Missing values: -9999

---

## 2. API Requirements

### 2.1 Validation (400)
- Station ID numeric
- Valid date
- Valid year
- No conflicting params

### 2.2 Data Handling (404)
- Missing file
- No matching data

### 2.3 Success (200)
- Return structured JSON

---

## 3. Error Handling

- 400 → invalid input
- 404 → no data
- 500 → internal error

UI:
- Inline friendly message when API returns 400/404 for user-entered parameters
- 500 → /error page

---

## 4. UI Requirements

- Simple HTML
- Dropdowns, inputs, tables, charts
- No complex frameworks

---

## 5. Chart Requirements

- Data from API
- Dynamic updates
- Proper labeling

---

## 6. Non-Functional Requirements

- Caching (LRU)
- Scalable to 25k stations
- Logging + rotation
- Env-based config
- OS-independent paths
- Handle -9999 values