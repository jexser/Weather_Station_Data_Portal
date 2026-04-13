# Weather Station Data Portal – Requirements v2.3

## 1. General Description

A Flask-based web application and RESTful API designed to provide access to historical temperature records from various weather stations stored in a distributed flat-file system.

The system consists of three main parts:
- Web Portal (UI)
- RESTful API
- Data Storage Layer

---

## 1.1 Web Portal

### 1.1.1 Home Page (`/`, `/home`)
- Displays stations with:
  - Pagination (500 stations per page; if request returns less than 500 stations, show all from resonse)
  - Search by station name (prefix match)
- Search returns matching stations (ID + name via API endpoint)

**API dependency:**
- `/api/v1/stations?page=X`
- `/api/v1/stations/search?name=...`

**Mockup:**

```
+--------------------------------------------------+
| Weather Data Portal                              |
+--------------------------------------------------+
| [Home] [Charts] [Insights] [Compare] [API Docs]  |
+--------------------------------------------------+
| Find station id by name [searchfield]            |
| -------------------------------------------------|
| Stations                                         |
| -------------------------------------------------|
| ID     | Name                                    |
| 000001 | Vilnius                                 |
| 000002 | Kaunas                                  |
| ...                                              |
+--------------------------------------------------+
```

---

### 1.1.2 API Documentation (`/api`)
- Lists endpoints and usage examples

**Mockup:**

```
+--------------------------------------------------+
| API Documentation                                |
+--------------------------------------------------+
| GET /api/v1/station/{id}?date=YYYY-MM-DD         |
| GET /api/v1/station/{id}?year=YYYY               |
| GET /api/v1/insights/{id}?type=...               |
| GET /api/v1/compare?stationA=&stationB=&year=    |
| GET /api/v1/stations?page=X                      |
| GET /api/v1/stations/search?name=...             |
+--------------------------------------------------+
```

---

### 1.1.3 Charts Page (`/charts`)

User inputs:
- Station
- Chart type
- Optional date

Charts:

1. **Yearly Trend**
   - Average temperature per year
   - Aggregated (1 point per year)

2. **Same Date Across Years**
   - Input: MM-DD
   - Output: temperature across years

**Mockup:**

```
+--------------------------------------------------+
| Charts                                           |
+--------------------------------------------------+
| Station: [Vilnius ▼]                             |
| Chart:   [Yearly Trend ▼]                        |
| Date:    [MM-DD]                                 |
|                                                  |
| [ Load Chart ]                                   |
+--------------------------------------------------+
|                  (Chart Area)                    |
+--------------------------------------------------+
```

---

### 1.1.4 Insights Page (`/insights`)

Supported insights:

- `hottest_year` → hottest year in dataset for requested station
- `coldest_year`→ coldest year in dataset for requested station
- `hottest_day` → hottest day in dataset for requested station
- `coldest_day` → coldest day in dataset for requested station
- `avg_for_date` → average temperature for selected MM-dd across all years for requested station
- `temp_variability` → standard deviation of daily temperatures for selected MM-dd across all years (excluding missing values) for requested station
- `missing_data_count` → number of missing records in dataset for requested station

**Mockup:**

```
+--------------------------------------------------+
| Insights                                         |
+--------------------------------------------------+
| Station: [Vilnius ▼]                             |
| Date (optional): [MM-DD]                         |
|                                                  |
| [ Load Insights ]                                |
+--------------------------------------------------+
| Hottest Year: 2019                               |
| Coldest Year: 1963                               |
| Avg Temp (07-11): 18.4°C                         |
| Variability (std): ±6.2°C                        |
| Missing Records: 12                              |
+--------------------------------------------------+
```

---

### 1.1.5 Compare Page (`/compare`)

User inputs:
- Station A
- Station B
- Year

API:
- `/api/v1/compare?stationA=&stationB=&year=`

Output:
- Union table by date
- Three columns table: date, temperature of Station A, temperature of Station B
- For missing data show NULL

**Mockup:**

```
+--------------------------------------------------+
| Compare Stations                                 |
+--------------------------------------------------+
| Station A: [Vilnius ▼]                           |
| Station B: [London ▼]                            |
| Year:      [2020]                                |
|                                                  |
| [ Compare ]                                      |
+--------------------------------------------------+
| Date       | Vilnius | London                    |
|------------|---------|---------------------------|
| 2020-01-01 | -2.1    | 3.2                       |
| ...                                            |
+--------------------------------------------------+
```

---

### 1.1.6 Error Page (`/error`)
- Only for 500 errors

**Mockup:**

```
+--------------------------------------------------+
| Internal Server Error                            |
+--------------------------------------------------+
| Something went wrong. Please try again later.    |
|                                                  |
| [ Go Home ]                                      |
+--------------------------------------------------+
```

---

## 1.2 RESTful API

### 1.2.1 Core Endpoint
GET `/api/v1/station/{stationid}`

Params:
- date
- year
  - if provided both, raise 400

---

### 1.2.2 Insights Endpoint
GET `/api/v1/insights/{stationid}`

Params:
- type
- optional date (format: MM-DD for day-specific queries)

---

### 1.2.3 Compare Endpoint
GET `/api/v1/compare`

Params:
- stationA
- stationB
- year

---

### 1.2.4 Station Listing Endpoint
GET `/api/v1/stations`
GET `/api/v1/stations/search`

---

### 1.2.5 Response Format

Success:
{
  "data": ...
}

Error:
{
  "error": {
    "status_code": 400,
    "message": "..."
  }
}

---

## 1.3 Data Storage

- Fixed-format text files with CSV payload
- Skip header lines: 
  - 17 header lines for index file
  - 20 header lines for stations data files
- Scale Factor: Raw TG values are in 0.1°C increments (e.g., 212 = 21.2°C)

Fields:
- TG → stored as integer, returned as float (1 decimal)
- DATE → stored as string, returned as YYYY-mm-dd (e.g. 18600101 = 1860-01-01)
- STAID → stored as integer, in file names utilized with zfill(6) (e.g. 199 = 000199)
- STANAME → stored as capitalized string (e.g. VAEXJOE)

Missing values:
- -9999 → treated as NULL (excluded from calculations)

---

## 2. API Requirements

### 2.1 Validation (400)
- Station ID numeric
- Valid date
- Valid year
- No conflicting params

---

### 2.2 Data Handling (404)
- Missing file
- No matching data

---

### 2.3 Success (200)
- Structured JSON

---

## 3. Error Handling

- 400 / 404 → inline in UI
- 500 → redirect to `/error`

---

## 4. UI Requirements

- Simple UI (HTML only)
- Pagination required
- Search field required

---

## 5. Chart Requirements

- Data must be aggregated (no raw daily flood)
- Yearly chart = 1 point per year, annual mean temperature (average of all valid daily temperatures in that year)
- Same-date chart = 1 point per year

---

## 6. Non-Functional Requirements

### 6.1 Performance
- LRU caching
- Avoid repeated file reads

### 6.2 Scalability
- Potential support of 25k stations, but initial deployment with 399 stations.
- Pagination mandatory

### 6.3 Missng Data Handling
- Replace -9999 with NULL
- Exclude from stats

### 6.4 File I/O Optimization
- Load stations index into memory at startup

### 6.5 Logging
- Enabled with rotation

### 6.6 Config
- Debug via env var

### 6.7 Portability
- OS-independent paths

---