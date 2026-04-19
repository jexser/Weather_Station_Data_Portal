from typing import Final
from pathlib import Path
import re
import dotenv, os


FIELD_TG: Final[str] = "TG"
FIELD_DATE: Final[str] = "DATE"
FIELD_STAID: Final[str] = "STAID"
FIELD_STANAME: Final[str] = "STANAME"

ROWS_TO_SKIP_INDEX: Final[int] = 17
ROWS_TO_SKIP_STATION: Final[int] = 20

#TODO: make env vars
INDEX_PAGE_SIZE: Final[int] = 30 #500 for prod
SEARCH_RESULTS_LIMIT: Final[int] = 10 #50 for prod

BASE_PATH: Final[Path] = Path(__file__).resolve().parent
DATA_DIR: Final[Path] = BASE_PATH / "data"

PATTERN_STATION_ID: Final[re.Pattern] = re.compile(r"^\d{1,6}$") # 1–6 digit station ID
PATTERN_YEAR: Final[re.Pattern] = re.compile(r"^\d{4}$") # 4 digit year
PATTERN_STATION_NAME: Final[re.Pattern] = re.compile(r"^[A-Za-z\s'.-]+$") # Station name with letters, space, dash, apostrophe, dot
