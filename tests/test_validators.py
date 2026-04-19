from errors import BadRequest, NotFound
import validators
import pytest
import pandas as pd


# validate_station_id(stationid: str) -> None
# ================================================

# @pytest.mark.unit
@pytest.mark.parametrize("station_id", [
    "",         # empty
    "1234567",  # too long
    "abc",      # letters
    "12a3",     # mixed
    "-123",     # negative
])
def test_validate_station_id_invalid_cases(station_id):
    with pytest.raises(BadRequest):
        validators.validate_station_id(station_id)


# @pytest.mark.unit
@pytest.mark.parametrize("station_id", [
    "1",
    "123",
    "123456",
])
def test_validate_station_id_valid(station_id):
    validators.validate_station_id(station_id) # should not raise


# @pytest.mark.unit
def test_validate_station_id_invalid_message():
    with pytest.raises(BadRequest) as exc:
        validators.validate_station_id("abc")
    assert str(exc.value) == "Invalid station ID format. Please provide a valid station ID."


# validate_file_existence(file_path: Path) -> None
# ================================================


# @pytest.mark.unit
def test_validate_file_existence_valid(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("data")
    validators.validate_file_existence(file)  # should not raise


# @pytest.mark.unit
def test_validate_file_existence_missing(tmp_path):
    file = tmp_path / "missing.txt"
    with pytest.raises(NotFound):
        validators.validate_file_existence(file)


# @pytest.mark.unit
def test_validate_file_existence_message(tmp_path):
    file = tmp_path / "missing.txt"
    with pytest.raises(NotFound) as exc:
        validators.validate_file_existence(file)
    assert str(exc.value) == "Station data not found."


# validate_date_and_year_args(date_str: str | None, year_str: str | None) -> None
# ================================================

# @pytest.mark.unit
def test_validate_date_and_year_args_invalid_both():
    with pytest.raises(BadRequest):
        validators.validate_date_and_year_args("2000-10-10", "2000")


# @pytest.mark.unit
def test_validate_date_and_year_args_invalid_none():
    with pytest.raises(BadRequest):
        validators.validate_date_and_year_args(None, None)


# @pytest.mark.unit
def test_validate_date_and_year_args_valid_date():
    validators.validate_date_and_year_args("2000-10-10", None)


# @pytest.mark.unit
def test_validate_date_and_year_args_valid_year():
    validators.validate_date_and_year_args(None, "2000")


# @pytest.mark.unit
def test_validate_date_and_year_args_invalid_both_message():
    with pytest.raises(BadRequest) as exc:
        validators.validate_date_and_year_args("2000-10-10", "2000")
    assert str(exc.value) == "Please provide one query parameter: either 'year' or 'date'"


# @pytest.mark.unit
def test_validate_date_and_year_args_invalid_none_message():
    with pytest.raises(BadRequest) as exc:
        validators.validate_date_and_year_args("2000-10-10", "2000")
    assert str(exc.value) == "Please provide one query parameter: either 'year' or 'date'"


# validate_date_format(date_str: str) -> datetime.datetime
# ================================================

# @pytest.mark.unit
@pytest.mark.parametrize("date", [
    "10-10",
    "1999",
    "1999-30-30",
    "2020-00-00",
    "10-10-2020",
    "----------",
    "abc"
])
def test_validate_date_format_invalid(date):
    with pytest.raises(BadRequest):
        validators.validate_date_format(date_str=date)


# @pytest.mark.unit
@pytest.mark.parametrize("date", [
    "2020-10-10",
    "2024-02-29"
])
def test_validate_date_format_valid(date):
    validators.validate_date_format(date_str=date) # should not raise


# @pytest.mark.unit
def test_validate_date_format_invalid_message():
    with pytest.raises(BadRequest) as exc:
        validators.validate_date_format(date_str="1999-30-30")
    assert str(exc.value) == "Invalid date, please provide a valid calendar date in the format YYYY-MM-DD"


# validate_year_format(year_str: str) -> None
# ================================================

# @pytest.mark.unit
@pytest.mark.parametrize("year", [
    "1",
    "11",
    "111",
    "11111",
    "abc",
    "11-1",
    "111O" # O instead of 0
])
def test_validate_year_format_invalid(year):
    with pytest.raises(BadRequest):
        validators.validate_year_format(year_str=year)

# @pytest.mark.unit
@pytest.mark.parametrize("year", [
    "1800",
    "2000",
    "2026"
])
def test_validate_year_format_valid(year):
    validators.validate_year_format(year)


# @pytest.mark.unit
def test_validate_year_format_invalid_message():
    with pytest.raises(BadRequest) as exc:
        validators.validate_year_format(year_str="11")
    assert str(exc.value) == "Invalid year format, please provide a 4-digit year"


# validate_temperature_data(temperature_series: Any) -> float
# ================================================

# @pytest.mark.unit
@pytest.mark.parametrize("input, expected", [
    (9.4, 9.4),
    (10.0, 10.0),
    (0.0, 0.0),
    (-10.0, -10.0)
])
def test_validate_temperature_valid(input, expected):
    assert validators.validate_temperature_data(input) == expected


# @pytest.mark.unit
def test_validate_temperature_pandas_nan():
    with pytest.raises(NotFound):
        validators.validate_temperature_data(pd.NA)


# @pytest.mark.unit
@pytest.mark.parametrize("value", [
    "abc",
    object(),
    [],          # list
    {},          # dict
])
def test_validate_temperature_invalid_types(value):
    with pytest.raises(NotFound):
        validators.validate_temperature_data(value)


# @pytest.mark.unit
def test_validate_temperature_series_multiple_values():
    series = pd.Series([1.0, 2.0])
    with pytest.raises(NotFound):
        validators.validate_temperature_data(series)


# @pytest.mark.unit
def test_validate_temperature_pandas_nan_message():
    with pytest.raises(NotFound) as exc:
        validators.validate_temperature_data(pd.NA)
    assert str(exc.value) == "No temperature data found"


# validate_page_number(page_str: str | None) -> int
# ================================================

# @pytest.mark.unit
def test_validate_page_number_none():
    with pytest.raises(BadRequest):
        validators.validate_page_number(None)


# @pytest.mark.unit
@pytest.mark.parametrize("page_str", ["abc", "1.5", "", "one"])
def test_validate_page_number_non_integer(page_str):
    with pytest.raises(BadRequest):
        validators.validate_page_number(page_str)


# @pytest.mark.unit
@pytest.mark.parametrize("page_str", ["0", "-1", "-100"])
def test_validate_page_number_less_than_one(page_str):
    with pytest.raises(BadRequest):
        validators.validate_page_number(page_str)


# @pytest.mark.unit
@pytest.mark.parametrize("page_str, expected", [
    ("1", 1),
    ("5", 5),
    ("100", 100),
])
def test_validate_page_number_valid(page_str, expected):
    assert validators.validate_page_number(page_str) == expected


# @pytest.mark.unit
def test_validate_page_number_none_message():
    with pytest.raises(BadRequest) as exc:
        validators.validate_page_number(None)
    assert str(exc.value) == "Please provide a page number"


# @pytest.mark.unit
def test_validate_page_number_non_integer_message():
    with pytest.raises(BadRequest) as exc:
        validators.validate_page_number("abc")
    assert str(exc.value) == "Page must be integer and >= 1"


# @pytest.mark.unit
def test_validate_page_number_less_than_one_message():
    with pytest.raises(BadRequest) as exc:
        validators.validate_page_number("0")
    assert str(exc.value) == "Page must be integer and >= 1"


# validate_station_name(station_name: str) -> None
# ================================================

# @pytest.mark.unit
@pytest.mark.parametrize("name", [
    "123",
    "Station!",
    "Name@Place",
    "Test#1",
])
def test_validate_station_name_invalid(name):
    with pytest.raises(BadRequest):
        validators.validate_station_name(name)


# @pytest.mark.unit
@pytest.mark.parametrize("name", [
    "London",
    "De Bilt",
    "St. Petersburg",
    "Clermont-Ferrand",
    "O'Brien",
])
def test_validate_station_name_valid(name):
    validators.validate_station_name(name)  # should not raise


# @pytest.mark.unit
def test_validate_station_name_invalid_message():
    with pytest.raises(BadRequest) as exc:
        validators.validate_station_name("Bad!Name")
    assert str(exc.value) == "Provide correct name; Allowed characters: Letters, space, dash, apostrophe, dot"