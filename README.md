# Weather Station Data Portal

A Flask-based web application and RESTful API designed to provide access to historical temperature data from various weather stations stored in flat-file format.

## 🚀 Overview

This project serves two primary purposes:
1.  **Web Portal**: A user-friendly interface to browse a list of available weather stations.
2.  **RESTful API**: A programmatic way to query specific temperature records for a given station on a specific date.

The application reads directly from a local data directory (`data_small/`), making it highly efficient for serving pre-processed historical datasets without the need for a heavy database engine.

## 📂 Project Structure

```text
.
├── main.py              # Flask application logic and API endpoints
├── README.md            # Project documentation
├── data_small/          # Data repository
│   ├── stations.txt     # Master list of weather stations (ID and Name)
│   └── TG_STAIDXXXXXX.txt # Individual temperature record files per station
├── templates/           # HTML templates
│   └── home.html       # Main dashboard view
└── static/              # Static assets (CSS, JS, Images)
```

## 🛠️ Technical Stack

*   **Language**: Python 3.x
*   **Web Framework**: [Flask](https://flask.palletsprojects.com/)
*   **Data Processing**: [Pandas](https://pandas.pydata.org/)
*   **Templating Engine**: Jinja2

## ⚙️ How It Works

### Data Storage Format
The system relies on a structured flat-file architecture:
*   **Stations Metadata**: `stations.txt` contains the registry of all stations.
*   **Temperature Records**: Each station has its own file (e.g., `TG_STAID000001.txt`). These files contain time-series data where temperature values are stored as integers (multiplied by 10) to maintain precision without floating-point issues in text format.

### Web Interface
When accessing the root URL (`/`):
1.  The app parses `stations.txt`, skipping metadata headers.
2.  It extracts Station IDs and Names.
3.  It renders an HTML table showing all available stations.

### API Endpoints

#### Get Temperature by Station and Date
Retrieves the temperature for a specific station on a requested date.

**Endpoint:** `GET /api/v1/<stationid>/<date>`

**Parameters:**
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `stationid` | string | The 6-digit zero-padded station ID (e.g., `000001`) |
| `date` | string | The date in `YYYY-MM-DD` format |

**Example Request:**
`GET /api/v1/000001/2023-01-01`

**Example Response (JSON):**
```json
{
  "stationid": "000001",
  "date": "2023-01-01",
  "temperature": 12.5
}
```

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
```
The application will start a development server at `http://127.0.0.1:5000`.

## 📝 Note on Data Parsing
The application uses a `Fields` dataclass to handle inconsistent column naming in the raw text files (e.g., handling extra whitespace in headers like `"    DATE"`). It also performs automatic scaling, dividing temperature values by 10 during retrieval to return standard Celsius values.
```