Module 1: Station Management & Discovery
As a user, I need to browse and search available weather stations so that I can select a location for analysis.

User Story 1: Station Browsing with Pagination
Requirement 1: Home page displays paginated station list.
Acceptance Criteria:
1.1. /api/v1/stations?page=X returns up to 500 stations per page with total_pages, page, and per_page metadata.
1.2. Frontend shows Next/Previous controls and current page.
1.3. Requests for pages beyond range return empty list and appropriate metadata.

User Story 2: Station Search (Prefix Match)
Requirement 1: Implement prefix-search by station name.
Acceptance Criteria:
2.1. /api/v1/stations/search?name=PREFIX returns stations whose names start with PREFIX (case-insensitive).
2.2. Search results include stationid and staname.
2.3. Search uses in-memory index and responds within acceptable latency (<300ms under normal load).

Module 2: Charts & Visualization
As a user, I need aggregated chart data so that I can view trends without overloading the browser.

User Story 3: Yearly Trend Chart Data
Requirement 1: Provide annual mean temperatures for charts.
Acceptance Criteria:
3.1. Yearly trend returns one point per year: the annual mean (average of all valid daily temperatures for that year).
3.2. Values exclude -9999 (treated as NULL) from calculations.
3.3. Returned temperatures are floats with one decimal.

User Story 4: Same-Date-Across-Years Chart Data
Requirement 1: Provide day-specific series across years.
Acceptance Criteria:
4.1. Client supplies MM-DD; API validates format and returns 400 for invalid input.
4.2. Response includes one value per year representing that day's temperature (or null if missing).
4.3. Endpoint documented as part of /api/v1/insights/{stationid} with type=avg_for_date or equivalent.

Module 3: Insights & Analytics
As an analyst, I need computed statistics so that I can report extremes and variability for a station.

User Story 5: Core Insights Endpoint (Types)
Requirement 1: Support named insight types via /api/v1/insights/{stationid}.
Acceptance Criteria:
5.1. Supported type values: hottest_year, coldest_year, hottest_day, coldest_day, avg_for_date, temp_variability, missing_data_count.
5.2. Requests with unknown type return 400 with a clear message.
5.3. All insights exclude -9999 values.

User Story 6: Day-Specific Insights with MM-DD
Requirement 1: MM-DD day queries produce per-year results.
Acceptance Criteria:
6.1. date param must be MM-DD; invalid formats return 400.
6.2. avg_for_date with MM-DD returns temperatures per year for that day and years_covered metadata.
6.3. Response includes missing_data_count for the requested scope.

User Story 7: Statistical Definitions & Outputs
Requirement 1: Define and return computed metrics unambiguously.
Acceptance Criteria:
7.1. temp_variability returns the standard deviation of daily temperatures (excluding NULLs), rounded to one decimal.
7.2. hottest_year/coldest_year return the year and the annual mean temp (1 decimal).
7.3. hottest_day/coldest_day return full date (YYYY-MM-DD) and temperature (1 decimal).

Module 4: Comparison Feature
As a user, I need to compare two stations for a year so that I can view side-by-side temperature differences.

User Story 8: Compare Endpoint
Requirement 1: Implement /api/v1/compare?stationA=&stationB=&year=.
Acceptance Criteria:
8.1. Response is a date-ordered array with {date, stationA_temp, stationB_temp} for each day of the year.
8.2. Missing values become null in the returned rows.
8.3. Include summary with counts: valid_days_stationA, missing_days_stationA, valid_days_stationB, missing_days_stationB.
8.4. If both stations have no data for the year, return 404.

Module 5: Core Station Data API
As a developer, I need a stable core endpoint to fetch raw or scoped station data.

User Story 9: Core Station Data Endpoint
Requirement 1: GET /api/v1/station/{stationid} supports date (YYYY-MM-DD) and year (YYYY) parameters.
Acceptance Criteria:
9.1. date=YYYY-MM-DD returns that date record or 404 if missing.
9.2. year=YYYY returns all records for that year (subject to chart aggregation rules).
9.3. Supplying both date and year returns 400 (conflicting parameters).
9.4. stationid accepted as integer; server resolves files using str(stationid).zfill(6).

Module 6: Station Listing & Indexing
As an operator, I need an efficient station index so that listing and search are fast and memory-bounded.

User Story 10: Stations Index Load & Pagination Backend
Requirement 1: Load and use an in-memory stations index at startup for listings and searches.
Acceptance Criteria:
10.1. Index file is parsed at startup (skip 17 preamble lines).
10.2. /api/v1/stations returns paginated results using the in-memory index.
10.3. Index refresh strategy documented (e.g., restart to reload or admin endpoint).

Module 7: Data Storage, Parsing & Conversion
As an engineer, I need reliable parsing and conversion rules for the raw files so that downstream computations are correct.

User Story 11: File Parsing, TG Conversion, and Missing Data Handling
Requirement 1: Parse station files, apply scale factor, and nullify missing sentinels.
Acceptance Criteria:
11.1. Skip 20 header lines for station data files and parse CSV payload consistently.
11.2. Convert raw TG integers to floats with one decimal using a 0.1°C scale factor (e.g., 212 → 21.2).
11.3. Replace -9999 with null (or pd.NA) and exclude from aggregations.
11.4. All parsing errors produce logged warnings and result in a 500 for requests that cannot be served.

Module 8: Non-Functional & Operational Requirements
As an operator, I need caching, logging, and config controls so the service performs reliably at scale.

User Story 12: Caching, Logging, and Configuration
Requirement 1: Implement LRU caching, rotating logs, and env-based config.
Acceptance Criteria:
12.1. LRU cache for recent station data and computed insights with configurable max size and TTL.
12.2. Logging includes timestamps, request IDs, and rotates by size/time.
12.3. Debug and other behavior toggles controlled via environment variables.
12.4. File path handling uses OS-independent APIs (e.g., pathlib).

Module 9: Error Handling & UX
As a user, I need clear error behaviors so that the UI shows helpful messages without unnecessary navigation.

User Story 13: Error Handling Contract
Requirement 1: API and UI must follow the documented error handling behavior.
Acceptance Criteria:
13.1. API returns 400 for validation errors, 404 for missing data, 500 for internal errors, using the standardized error JSON.
13.2. Frontend displays inline messages for 400/404 and redirects to /error only for 500.
13.3. Error responses include status_code, message, and optionally details.