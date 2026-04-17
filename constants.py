from typing import Final
from pathlib import Path
# import dotenv, os

# dotenv.load_dotenv()

FIELD_TG: Final[str] = "TG"
FIELD_DATE: Final[str] = "DATE"
FIELD_STAID: Final[str] = "STAID"
FIELD_STANAME: Final[str] = "STANAME"

ROWS_TO_SKIP_INDEX: Final[int] = 17
ROWS_TO_SKIP_STATION: Final[int] = 20

#TODO: make env vars
INDEX_PAGE_SIZE: Final[int] = 20 #500 for prod
MAX_SEARCH_RESULTS: Final[int] = 10 #50 for prod

BASE_PATH: Final[Path] = Path(__file__).resolve().parent
DATA_DIR: Final[Path] = BASE_PATH / "data"