    
# 18.3. hottest_year and coldest_year return {"data": {"year": }}
def _get_hottest_year():
    pass


# 18.3. hottest_year and coldest_year return {"data": {"year": }}
def _get_coldest_year():
    pass


# 18.4. hottest_day and coldest_day return {"data": {"date": "YYYY-MM-DD", "TG": }}
def _get_hottest_day():
    pass

# 18.4. hottest_day and coldest_day return {"data": {"date": "YYYY-MM-DD", "TG": }}
def _get_coldest_day():
    pass


# 18.5. avg_for_date and temp_variability require the date parameter in MM-DD format; \
#  omitting it returns 400 with message "Parameter 'date' (MM-DD) is required for this insight type."
# 18.6. avg_for_date returns {"data": {"avg_temp": }} rounded to 1 decimal; -9999 values excluded.
def _get_avg_for_date(date_mm_dd: str):
    pass


# avg_for_date and temp_variability require the date parameter in MM-DD format; \
#  omitting it returns 400 with message "Parameter 'date' (MM-DD) is required for this insight type."
# 18.7. temp_variability returns {"data": {"std_dev": }} rounded to 1 decimal; -9999 values excluded.
def _get_temp_variability(date_mm_dd: str):
    pass


# 18.8. missing_data_count returns {"data": {"missing_count": }} representing the count of -9999 entries in the station file.
def _get_missing_data_count():
    pass