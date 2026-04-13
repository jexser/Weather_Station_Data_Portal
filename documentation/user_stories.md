# Software Requirements Specification: Weather Station Data Portal
> as per Requirements v2.3

## 📋 Project Overview
A Flask-based web application and RESTful API designed to provide access to historical temperature records from various weather stations stored in a distributed flat-file system. The system provides high-performance data retrieval, statistical insights, and visual comparisons of historical climate trends.

---

## ⚡ Module 1: Home Page – Station Browser

As a portal user, I need to browse and search weather stations so that I can find a station ID to use in other parts of the application.

### User Story 1: Display Paginated Station List
- **Requirement**: The Home page (`/`, `/home`) must display a paginated table of all stations showing ID and Name, loading data from `GET /api/v1/stations?page=X`.
- **Acceptance Criteria**:
  - 1.1. The station table renders two columns: **ID** and **Name**.
  - 1.2. Each page displays up to 500 stations.
  - 1.3. If the API returns fewer than 500 stations, all returned stations are shown and no further pages are implied.
  - 1.4. Pagination controls (Previous / Next) are visible only when more than one page exists.
  - 1.5. The currently active page number is visually indicated.
  - 1.6. Navigating to a new page replaces the current table contents with the new page's results.

### User Story 2: Search Stations by Name (Combobox)
- **Requirement**: The Home page must provide a combobox that lets users type a partial station name, query the search API, and select from returned results.
- **Acceptance Criteria**:
  - 2.1. A search input field is present above the station table with a Search / Enter trigger.
  - 2.2. On submit, the UI calls `GET /api/v1/stations/search?name=<input>` with the user's text.
  - 2.3. The search is case-insensitive and accepts partial (prefix) matches.
  - 2.4. The API returns a maximum of 50 matching results; the UI renders all returned results in a selectable list below the input.
  - 2.5. The user can select a result from the list; the selected station's ID and Name are displayed in the table (replacing the paginated view).
  - 2.6. If the search returns zero results, the list displays a "No stations found" message.
  - 2.7. Clearing the search input and re-submitting restores the default paginated station list.

---

## ⚡ Module 2: API Documentation Page

As a developer or technical user, I need a reference page listing all available API endpoints so that I can integrate with or manually query the API without consulting external documentation.

### User Story 3: Display API Endpoint Reference
- **Requirement**: The `/api` page must list all available endpoints with their parameters and usage examples.
- **Acceptance Criteria**:
  - 3.1. The page is accessible at `/api` and linked from the main navigation.
  - 3.2. The following endpoints are documented: `GET /api/v1/station/{id}?date=`, `GET /api/v1/station/{id}?year=`, `GET /api/v1/insights/{id}?type=`, `GET /api/v1/compare?stationA=&stationB=&year=`, `GET /api/v1/stations?page=X`, `GET /api/v1/stations/search?name=`.
  - 3.3. Each endpoint entry shows: HTTP method, path, accepted parameters, and at least one usage example.
  - 3.4. Both success and error response envelope shapes are documented with example JSON.
  - 3.5. The page is static HTML — no API calls are made to render it.

---

## ⚡ Module 3: Charts Page

As a portal user, I need to visualize temperature trends for a selected station so that I can identify patterns over time.

### User Story 4: Station Selection via Combobox on Charts Page
- **Requirement**: The Charts page must provide the same combobox search-and-select pattern as the Home page to allow station selection before loading a chart.
- **Acceptance Criteria**:
  - 4.1. A combobox input is present on the Charts page; the user types a partial name and presses Search / Enter.
  - 4.2. `GET /api/v1/stations/search?name=<input>` is called; up to 50 results are shown in a selectable dropdown list.
  - 4.3. The user must select a station from the list before the Load Chart button becomes active.
  - 4.4. The selected station's name is shown in the combobox field after selection.

### User Story 5: Yearly Trend Chart
- **Requirement**: When chart type "Yearly Trend" is selected, the system must render a chart showing one data point per year representing the annual mean temperature for the selected station.
- **Acceptance Criteria**:
  - 5.1. The chart type dropdown includes "Yearly Trend" as an option.
  - 5.2. On Load Chart, the UI calls `GET /api/v1/station/{id}?year=` iteratively or a suitable aggregation endpoint to retrieve per-year data; each year is aggregated to a single mean value (average of all valid daily temperatures, excluding `-9999` values).
  - 5.3. The chart renders exactly one point per year on the x-axis; the y-axis represents temperature in °C.
  - 5.4. Years with zero valid records are omitted from the chart.
  - 5.5. The Date input field is hidden or disabled when "Yearly Trend" is selected.

### User Story 6: Same Date Across Years Chart
- **Requirement**: When chart type "Same Date Across Years" is selected, the system must render a chart showing the temperature recorded on a specific MM-DD for each available year.
- **Acceptance Criteria**:
  - 6.1. The chart type dropdown includes "Same Date Across Years" as an option.
  - 6.2. Selecting this chart type activates the Date input field, which accepts `MM-DD` format only.
  - 6.3. On Load Chart, the UI calls the appropriate API to retrieve temperature for the specified `MM-DD` across all years.
  - 6.4. The chart renders one point per year where a record exists for that date; years with missing (`-9999`) or absent records are omitted.
  - 6.5. If no date is entered and the user clicks Load Chart, an inline validation message "Please enter a date (MM-DD)" is shown and no API call is made.
  - 6.6. The x-axis represents year; the y-axis represents temperature in °C.

---

## ⚡ Module 4: Insights Page

As a portal user, I need to retrieve statistical insights for a selected station so that I can understand historical temperature extremes and data quality.

### User Story 7: Station Selection via Combobox on Insights Page
- **Requirement**: The Insights page must provide the same combobox search-and-select pattern for station selection.
- **Acceptance Criteria**:
  - 7.1. A combobox input is present; partial name search triggers `GET /api/v1/stations/search?name=<input>` returning up to 50 results.
  - 7.2. The user must select a station before the Load Insights button becomes active.

### User Story 8: Load and Display All Insights
- **Requirement**: On Load Insights, the system must call `GET /api/v1/insights/{id}?type=<type>` for each insight type and render results in a structured results panel.
- **Acceptance Criteria**:
  - 8.1. Clicking Load Insights triggers API calls for all seven insight types: `hottest_year`, `coldest_year`, `hottest_day`, `coldest_day`, `avg_for_date`, `temp_variability`, `missing_data_count`.
  - 8.2. Each insight is displayed as a labelled row in the results panel.
  - 8.3. Results for `hottest_year` and `coldest_year` display the year value.
  - 8.4. Results for `hottest_day` and `coldest_day` display the full date and temperature in °C.
  - 8.5. Results for `avg_for_date` display the average temperature in °C formatted to one decimal place.
  - 8.6. Results for `temp_variability` display the standard deviation in °C formatted to one decimal place, prefixed with `±`.
  - 8.7. Results for `missing_data_count` display the integer count of missing records.

### User Story 9: Date-Dependent Insight Rows (No Date Provided)
- **Requirement**: Insights that require a `MM-DD` date (`avg_for_date`, `temp_variability`) must render in a grayed-out state with a tooltip when no date is provided, rather than being hidden or erroring.
- **Acceptance Criteria**:
  - 9.1. If no date is entered in the optional Date field, the rows for `avg_for_date` and `temp_variability` are rendered with grayed-out placeholder text (e.g., "—") instead of a value.
  - 9.2. A tooltip on hover for those rows reads: "Provide a date (MM-DD) to get this insight."
  - 9.3. The API is **not** called for date-dependent insights when no date is supplied.
  - 9.4. If a valid `MM-DD` date is entered, the grayed-out state is removed and the API is called for those two insights on Load Insights.
  - 9.5. If an invalid date format is entered, an inline validation message is shown and the date-dependent rows remain grayed out.

---

## ⚡ Module 5: Compare Page

As a portal user, I need to compare daily temperature records between two stations for a given year so that I can analyze differences side by side.

### User Story 10: Station Selection for Comparison
- **Requirement**: The Compare page must provide two independent combobox inputs for Station A and Station B using the same search-and-select pattern.
- **Acceptance Criteria**:
  - 10.1. Two separate combobox inputs are present, labelled "Station A" and "Station B".
  - 10.2. Each combobox independently calls `GET /api/v1/stations/search?name=<input>` and displays up to 50 results.
  - 10.3. The Compare button becomes active only when both stations and a year are selected/entered.
  - 10.4. The same station may be selected for both A and B (no restriction); results will be identical columns.

### User Story 11: Display Side-by-Side Temperature Comparison Table
- **Requirement**: On Compare, the system must call `GET /api/v1/compare?stationA=&stationB=&year=` and render a full-year union table with one row per day.
- **Acceptance Criteria**:
  - 11.1. The results table has three columns: **Date**, **Station A name**, **Station B name**.
  - 11.2. The table contains a row for every calendar date in the requested year (365 or 366 rows), as generated by the API's full date range.
  - 11.3. Temperature values are displayed as floats with one decimal place and the `°C` unit.
  - 11.4. Missing values are displayed as `NULL` in the respective cell.
  - 11.5. Dates where both stations have `NULL` are still shown as rows (full date range preserved).
  - 11.6. The table is scrollable; column headers remain visible while scrolling.

---

## ⚡ Module 6: Error Handling (UI)

As a portal user, I need clear feedback when something goes wrong so that I understand what happened and what to do next.

### User Story 12: Inline 400 / 404 Error Display
- **Requirement**: API errors with status 400 or 404 must be displayed inline within the page where the request originated, without redirecting.
- **Acceptance Criteria**:
  - 12.1. When an API call returns 400, the error message from `error.message` is displayed inline near the triggering UI component.
  - 12.2. When an API call returns 404, a user-friendly message such as "No data found for the selected station / date." is displayed inline.
  - 12.3. The rest of the page remains functional; previously loaded data is not cleared by a new error.

### User Story 13: 500 Error Page
- **Requirement**: Any unhandled server error (HTTP 500) must redirect the user to a dedicated error page at `/error`.
- **Acceptance Criteria**:
  - 13.1. A Flask error handler catches all 500-level errors and redirects to `/error`.
  - 13.2. The `/error` page displays the message: "Something went wrong. Please try again later."
  - 13.3. A "Go Home" button links back to `/`.
  - 13.4. The `/error` page contains no dynamic content and makes no API calls.

---

## ⚡ Module 7: RESTful API – Core Endpoints

As a consuming client (UI or external), I need a well-validated REST API so that I can retrieve temperature data reliably with predictable responses.

### User Story 14: Retrieve Temperature by Date
- **Requirement**: `GET /api/v1/station/{stationid}?date=YYYY-MM-DD` must return the temperature record for a single date.
- **Acceptance Criteria**:
  - 14.1. A valid `date` parameter in `YYYY-MM-DD` format returns `{"data": {"date": "YYYY-MM-DD", "TG": <float>}}` with status 200.
  - 14.2. If the raw TG value is `-9999`, the response returns `{"data": {"date": "YYYY-MM-DD", "TG": null}}`.
  - 14.3. Supplying both `date` and `year` in the same request returns 400 with message `"Conflicting parameters: provide either 'date' or 'year', not both."`.
  - 14.4. A non-numeric `stationid` returns 400 with an appropriate message.
  - 14.5. An invalid date format returns 400 with message `"Invalid date format. Expected YYYY-MM-DD."`.
  - 14.6. A valid station ID with no file on disk returns 404.
  - 14.7. A valid station and date with no matching record returns 404.

### User Story 15: Retrieve Temperature Records by Year
- **Requirement**: `GET /api/v1/station/{stationid}?year=YYYY` must return all daily temperature records for the specified year.
- **Acceptance Criteria**:
  - 15.1. A valid `year` parameter returns `{"data": [{"date": "YYYY-MM-DD", "TG": <float|null>}, ...]}` with status 200.
  - 15.2. Raw TG values of `-9999` are returned as `null` in the array.
  - 15.3. If the station exists but has zero records for the requested year, the response is `{"data": []}` with status 200.
  - 15.4. A non-numeric or invalid year (e.g., `year=abcd`) returns 400.
  - 15.5. A station file that does not exist returns 404.

### User Story 16: Station Listing with Pagination
- **Requirement**: `GET /api/v1/stations?page=X` must return a paginated list of station IDs and names.
- **Acceptance Criteria**:
  - 16.1. Each page returns up to 500 stations as `{"data": [{"id": "000001", "name": "Vilnius"}, ...]}`.
  - 16.2. Station IDs are zero-padded to 6 digits (e.g., `"000001"`).
  - 16.3. Station names are returned as stored (capitalized string).
  - 16.4. If `page` is omitted, page 1 is assumed.
  - 16.5. Requesting a page beyond the last available page returns `{"data": []}` with status 200.
  - 16.6. The stations index is loaded into memory at application startup and served from cache on every request.

### User Story 17: Station Search Endpoint
- **Requirement**: `GET /api/v1/stations/search?name=<query>` must return up to 50 stations whose names match the partial query, case-insensitively.
- **Acceptance Criteria**:
  - 17.1. Returns `{"data": [{"id": "...", "name": "..."}, ...]}` with status 200.
  - 17.2. Matching is case-insensitive; `"vil"` matches `"VILNIUS"`.
  - 17.3. Partial matches anywhere in the name are accepted (not strictly prefix-only, consistent with section 1.1.1).
  - 17.4. Results are capped at 50 entries.
  - 17.5. If no stations match, `{"data": []}` is returned with status 200.
  - 17.6. A missing or empty `name` parameter returns 400 with message `"Parameter 'name' is required."`.

---

## ⚡ Module 8: RESTful API – Insights & Compare Endpoints

As a consuming client, I need insights and comparison data exposed via API so that the UI and any external consumers can retrieve aggregated statistics.

### User Story 18: Insights Endpoint
- **Requirement**: `GET /api/v1/insights/{stationid}?type=<type>&date=<MM-DD>` must return the requested statistical insight for the station.
- **Acceptance Criteria**:
  - 18.1. Supported `type` values: `hottest_year`, `coldest_year`, `hottest_day`, `coldest_day`, `avg_for_date`, `temp_variability`, `missing_data_count`.
  - 18.2. An unsupported `type` value returns 400 with message `"Invalid insight type."`.
  - 18.3. `hottest_year` and `coldest_year` return `{"data": {"year": <int>}}`.
  - 18.4. `hottest_day` and `coldest_day` return `{"data": {"date": "YYYY-MM-DD", "TG": <float>}}`.
  - 18.5. `avg_for_date` and `temp_variability` require the `date` parameter in `MM-DD` format; omitting it returns 400 with message `"Parameter 'date' (MM-DD) is required for this insight type."`.
  - 18.6. `avg_for_date` returns `{"data": {"avg_temp": <float>}}` rounded to 1 decimal; `-9999` values excluded.
  - 18.7. `temp_variability` returns `{"data": {"std_dev": <float>}}` rounded to 1 decimal; `-9999` values excluded.
  - 18.8. `missing_data_count` returns `{"data": {"missing_count": <int>}}` representing the count of `-9999` entries in the station file.
  - 18.9. A station file that does not exist returns 404.

### User Story 19: Compare Endpoint
- **Requirement**: `GET /api/v1/compare?stationA=<id>&stationB=<id>&year=<YYYY>` must return a full-year union of daily temperatures for both stations.
- **Acceptance Criteria**:
  - 19.1. Returns `{"data": [{"date": "YYYY-MM-DD", "stationA": <float|null>, "stationB": <float|null>}, ...]}` with status 200.
  - 19.2. The response contains a row for every calendar date in the requested year (365 or 366 entries), regardless of whether either station has data for that date.
  - 19.3. Missing or `-9999` values are returned as `null`.
  - 19.4. Missing `stationA`, `stationB`, or `year` parameters each return 400 with a descriptive message.
  - 19.5. A non-numeric station ID or invalid year returns 400.
  - 19.6. If either station file does not exist, return 404 specifying which station was not found.

---

## ⚡ Module 9: Data Storage & File I/O Layer

As a backend developer, I need a reliable and optimized data access layer so that the application reads flat files correctly, handles missing data gracefully, and performs well under load.

### User Story 20: Parse Station Index File
- **Requirement**: At application startup, the `stations.txt` index file must be read, parsed, and held in memory for the lifetime of the process.
- **Acceptance Criteria**:
  - 20.1. The first 17 header lines of `stations.txt` are skipped during parsing.
  - 20.2. Each subsequent line is parsed to extract STAID (integer) and STANAME (string).
  - 20.3. STAID is zero-padded to 6 digits for use in file lookups and API responses.
  - 20.4. The in-memory structure supports O(1) or O(log n) lookup by ID and case-insensitive partial search by name.
  - 20.5. If `stations.txt` is missing at startup, the application logs a critical error and exits with a non-zero code.

### User Story 21: Parse Station Temperature Files
- **Requirement**: Individual station data files (`TG_STAIDXXXXXX.txt`) must be parsed on-demand with results cached to avoid repeated file I/O.
- **Acceptance Criteria**:
  - 21.1. The first 20 header lines of each station file are skipped during parsing.
  - 21.2. The DATE field is converted from `YYYYMMDD` integer string to `YYYY-MM-DD` string format.
  - 21.3. The TG field is divided by 10.0 to convert from 0.1°C increments to °C float; value `-9999` is stored/returned as `null`.
  - 21.4. STAID in file names uses `zfill(6)` padding (e.g., station `199` → file `TG_STAID000199.txt`).
  - 21.5. File paths are constructed using OS-independent path joining (e.g., `os.path.join` or `pathlib`).
  - 21.6. Parsed file results are stored in an LRU cache keyed by station ID; repeated requests for the same station do not re-read the file.
  - 21.7. If a station file does not exist, a `FileNotFoundError` (or equivalent) is raised and mapped to a 404 API response.

---

## ⚡ Module 10: Non-Functional & Operational Requirements

As a system operator, I need the application to be observable, configurable, and portable so that it can be deployed and maintained reliably.

### User Story 22: Logging with Rotation
- **Requirement**: The application must emit structured logs for all requests, errors, and significant events, with log rotation configured.
- **Acceptance Criteria**:
  - 22.1. All HTTP requests are logged with method, path, status code, and response time.
  - 22.2. All unhandled exceptions are logged with a full stack trace.
  - 22.3. Log rotation is configured (e.g., `RotatingFileHandler`) with a maximum file size and backup count.
  - 22.4. Log level is configurable via environment variable (e.g., `LOG_LEVEL=DEBUG`).

### User Story 23: Debug Mode Configuration
- **Requirement**: Flask debug mode must be controlled exclusively via an environment variable, not hardcoded.
- **Acceptance Criteria**:
  - 23.1. The application reads a `DEBUG` (or equivalent) environment variable at startup.
  - 23.2. If `DEBUG=true`, Flask runs in debug mode with hot-reload enabled.
  - 23.3. If the variable is absent or set to any other value, debug mode is off.
  - 23.4. Debug mode is never enabled in a production environment by default.