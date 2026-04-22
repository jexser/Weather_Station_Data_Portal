import repositories.station_repository as station_repository
from errors import NotFound
import constants
import repositories.station_repository as station_repository
import models

# 18.3. hottest_year and coldest_year return {"data": {"year": }}
def _get_hottest_year(stationid: str, date_mm_dd: str | None):
    df = station_repository._load_station(stationid=stationid).copy()
    year_avg = df.groupby(df[constants.FIELD_DATE].dt.year)[constants.FIELD_TG].mean()
    hottest_year = int(year_avg.idxmax())
    
    payload = {"data": {"year": hottest_year}}
    return payload


# 18.3. hottest_year and coldest_year return {"data": {"year": }}
def _get_coldest_year(stationid: str, date_mm_dd: str | None):
    df = station_repository._load_station(stationid=stationid).copy()
    year_avg = df.groupby(df[constants.FIELD_DATE].dt.year)[constants.FIELD_TG].mean()
    coldest_year = int(year_avg.idxmin())
    payload = {"data": {"year": coldest_year}}
    return payload


# 18.4. hottest_day and coldest_day return {"data": {"date": "YYYY-MM-DD", "TG": }}
def _get_hottest_day(stationid: str, date_mm_dd: str | None):
    df = station_repository._load_station(stationid=stationid).copy()
    row = df.loc[df[constants.FIELD_TG] == df[constants.FIELD_TG].max()].iloc[0]
    date = row[constants.FIELD_DATE].strftime("%Y-%m-%d")
    temperature = float(row[constants.FIELD_TG])
    
    payload = {"data": {"date": date, "TG": temperature}}
    return payload



# 18.4. hottest_day and coldest_day return {"data": {"date": "YYYY-MM-DD", "TG": }}
def _get_coldest_day(stationid: str, date_mm_dd: str | None):
    df = station_repository._load_station(stationid=stationid).copy()
    row = df.loc[df[constants.FIELD_TG] == df[constants.FIELD_TG].min()].iloc[0]
    date = row[constants.FIELD_DATE].strftime("%Y-%m-%d")
    temperature = float(row[constants.FIELD_TG])
    
    payload = {"data": {"date": date, "TG": temperature}}
    return payload



# 18.5. avg_for_date and temp_variability require the date parameter in MM-DD format; \
#  omitting it returns 400 with message "Parameter 'date' (MM-DD) is required for this insight type."
# 18.6. avg_for_date returns {"data": {"avg_temp": }} rounded to 1 decimal; -9999 values excluded.
def _get_avg_for_date(stationid: str, date_mm_dd: str | None):
    df = station_repository._load_station(stationid=stationid).copy()
    filtered = df[df[constants.FIELD_DATE].dt.strftime("%m-%d") == date_mm_dd]
    if filtered.empty:
        raise NotFound("No data for given date")
    temperature = round(float(filtered[constants.FIELD_TG].mean()), 1)
    
    payload = {"data": {"avg_temp": temperature}}
    return payload
    


# 18.5. avg_for_date and temp_variability require the date parameter in MM-DD format; \
#  omitting it returns 400 with message "Parameter 'date' (MM-DD) is required for this insight type."
# 18.7. temp_variability returns {"data": {"std_dev": }} rounded to 1 decimal; -9999 values excluded.
def _get_temp_variability(stationid: str, date_mm_dd: str | None):
    df = station_repository._load_station(stationid=stationid).copy()
    filtered = df[df[constants.FIELD_DATE].dt.strftime("%m-%d") == date_mm_dd]
    if filtered.empty:
        raise NotFound("No data for given date")
    temperature = round(float(filtered[constants.FIELD_TG].std()), 1)
    
    payload = {"data": {"std_dev": temperature}}
    return payload


# 18.8. missing_data_count returns {"data": {"missing_count": }} representing the count of -9999 entries in the station file.
def _get_missing_data_count(stationid: str, date_mm_dd: str | None):
    df = station_repository._load_station(stationid=stationid).copy()
    missing_count = int(df[constants.FIELD_TG].isna().sum())
    
    payload = {"data": {"missing_count": missing_count}}
    return payload