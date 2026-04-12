# Weather API Project – Requirements v2.2

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
  - Pagination (500 stations per page)
  - Search by station name
- Search returns matching stations (ID + name)

**API dependency:**
- `/api/v1/stations?page=X`
- `/api/v1/stations/search?name=...`

---

### 1.1.2 API Documentation (`/api`)
- Lists endpoints and examples

---

### 1.1.3 Charts Page (`/charts`)

User inputs:
- Station
- Chart type
- Optional date

Charts:

1. **Yearly Trend (restricted)**
   - Average temperature per year
   - Aggregated (1 point per year)

2. **Same Date Across Years**
   - Input: MM-DD
   - Output: temperature across years

---

### 1.1.4 Insights Page (`/insights`)

Supported insights:

- `hottest_year`
- `coldest_year`
- `hottest_day`
- `coldest_day`
- `avg_for_date`
- `temp_variability` → defined as standard deviation
- `missing_data_count`

---

### 1.1.5 Compare Page (`/compare`)

User inputs:
- Station A
- Station B
- Year

API:
- `/api/v1/compare?stationA=&stationB=&year=`

Output:
- Table by date

---

### 1.1.6 Error Page (`/error`)
- Only for 500 errors

---

## 1.2 RESTful API

### 1.2.1 Core Endpoint
GET `/api/v1/station/{stationid}`

Params:
- date
- year

---

### 1.2.2 Insights Endpoint
GET `/api/v1/insights/{stationid}`

Params:
- type
- optional date

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
- Skip header lines

Fields:
- TG → stored as integer, returned as float (1 decimal)
- DATE
- STAID
- STANAME

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
- Yearly chart = 1 point per year
- Same-date chart = 1 point per year

---

## 6. Non-Functional Requirements

### 6.1 Performance
- LRU caching
- Avoid repeated file reads

### 6.2 Scalability
- Support 25k stations
- Pagination mandatory

### 6.3 Data Handling
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

## 7. Definitions

- **Temperature Variability** = standard deviation of daily temperatures (excluding missing values)

---
