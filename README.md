# Weather Station Data Portal

A Flask-based web application and RESTful API designed to provide access to historical temperature records from various weather stations stored in a distributed flat-file system.

## Overview

This project serves two primary purposes:
1.  **Web Portal**: A user-friendly interface to browse a list of available weather stations via an HTML dashboard.
2.  **RESTful API**: A programmatic way to query specific temperature records using station IDs and optional filters (year or date).

The application is optimized for high-performance reads from local text files, performing real-time data cleaning and transformation.

## 📂 Project Structure

```text
.
├── .gitignore            # Git ignore rules
├── data_small/           # Data repository (Flat-file storage)
│   ├── .ipynb_checkpoints/
│   ├── stations.txt      # Master list of weather stations (Metadata)
│   └── TG_STAIDXXXXXX.txt # Individual temperature record files per station
├── logs/                 # Application logs
├── static/               # Static assets (CSS, JS, Images)
├── templates/            # HTML templates
│   └── home.html        # Main dashboard view
├── .env                  # Environment variables
├── errors.py             # Error handling utilities
├── main.py               # Flask application logic, API routing, and data processing
└── README.md             # Project documentation
```

## ⚙️ How It Works

### Data Processing Pipeline
The application uses a robust loading mechanism (`load_and_clean_data`) to handle the complexities of raw text files:
*   **Whitespace Stripping**: Automatically removes leading/trailing whitespace from all column headers to prevent `KeyError` during parsing.
*   **Temperature Scaling**: Converts temperature values from tenths of degrees (stored in text) to standard Celsius (floating point).
*   **Date Parsing**: Transforms raw date strings into Python `datetime` objects for accurate filtering and comparison.

### Web Interface
When accessing the root URL (`/`):
1.  The app parses `stations.txt`, skipping metadata headers.
2.  It extracts Station IDs and Names.
3.  It renders an HTML table showing all available stations.

### API Endpoints

#### Get Station Data
Retrieves temperature records for a specific station, optionally filtered by year or date.

**Endpoint:** `GET /api/v1/station/<stationid>`

**Path Parameters:**
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `stationid` | string | The 6-digit zero-padded station ID (e.g., `000001`) |

**Query Parameters (Optional):**
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `date` | string | A specific date in `YYYY-MM-DD` format. Returns a single temperature value. |
| `year` | string | A 4-digit year (e.g., `2023`). Returns all records for that year. |

**Example Requests:**
*   `GET /api/v1/station/000001?date=2023-05-20` $\rightarrow$ Returns temperature for that day.
*   `GET /api/v1/station/000001?year=2023` $\rightarrow$ Returns all records for 2023.

**Example JSON Response (Date Lookup):**
```json
{
  "stationid": "000001",
  "date": "2023-05-20", 
  "temperature": 15.2
}
```

### Error Handling
The API implements a comprehensive error handling strategy:
*   **`400 Bad Request`**: Returned for invalid station ID formats, malformed date strings (e.g., `2023-13-45`), or providing both `year` and `date` simultaneously.
*   **`404 Not Found`**: Returned if the requested station file does not exist on the server, or if a valid date/year was requested but contains no recorded data.
*   **`500 Internal Server Error`**: Returned for unexpected server-side errors.

## 🛠️ Technical Stack

*   **Language**: Python 3.x
*   **Web Framework**: [Flask](https://flask.palletsprojects.com/)
*   **Data Processing**: [Pandas](https://pandas.pydata.org/)
*   **Templating Engine**: Jinja2

## 🚀 Getting Started

### Prerequisites
*   Python 3.x
*   `pip` (Python package manager)

### Installation

1.  Clone the repository.
2.  Install required dependencies:
    ```bash
    pip install flask pandas
    ```

### Running the Application

Run the main script:
```bash
python main.py