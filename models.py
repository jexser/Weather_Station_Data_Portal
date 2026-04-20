from dataclasses import dataclass


@dataclass(frozen=True)
class StationRecord:
    station_id: str
    station_name: str


@dataclass(frozen=True)
class YearlyTemperatureRecord:
    year: int
    temperature: float | None


@dataclass(frozen=True)
class DailyTemperatureRecord:
    date: str
    temperature: float | None


@dataclass(frozen=True)
class PaginatedStations:
    stations: tuple[StationRecord, ...]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool


@dataclass(frozen=True)
class StationSearchResult:
    query: str
    stations: tuple[StationRecord, ...]
    limit: int


@dataclass(frozen=True)
class StationTemperatureResult:
    station_id: str
    date: str
    temperature: float


@dataclass(frozen=True)
class StationYearlyResult:
    station_id: str
    year: str
    records: tuple[DailyTemperatureRecord, ...]
