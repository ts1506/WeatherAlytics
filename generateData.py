#stub to inject data for testing purposes

from db.connection import add_weatherData
import time

# add_weatherData(reading_time, summary, precip_type, temperature, apparent_temperature, humidity, wind_speed, wind_bearing, visibility, pressure):

add_weatherData("2016-10-15 15:00:00", "Overcast", "", "20.233334", "19.2701", "0.47", "10.33", "249", "12.34", "1011.33")
time.sleep(4.5)
add_weatherData("2016-11-30 15:00:00", "Partly Cloudy", "", "19.233334", "18.5561", "0.34", "6.15", "249", "18.44", "1012.33")
time.sleep(4.5)
add_weatherData("2016-12-11 15:00:00", "Partly Cloudy", "rain", "19.233334", "16.2701", "0.49", "8.33", "249", "10.34", "1015.33")
time.sleep(4.5)
add_weatherData("2016-12-30 15:00:00", "Clear", "snow", "19.233334", "16.2701", "0.44", "8.33", "249", "10.34", "1015.33")
time.sleep(4.5)
add_weatherData("2017-01-06 15:00:00", "Clear", "", "17.233334", "14.2701", "0.23", "12.33", "249", "16.12", "1014.13")
time.sleep(4.5)
add_weatherData("2017-01-12 15:00:00", "Foggy", "rain", "21.34566", "18.3551", "0.45", "6.23", "251", "10.34", "1021.25")
time.sleep(4.5)
add_weatherData("2017-02-01 15:00:00", "Overcast", "rain", "19.4567", "16.8901", "0.61", "8.56", "249", "10.34", "1015.33")
