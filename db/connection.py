# Instructions for DB connection
"""
The connection string is stored in privatekeys.py, uncomment Line 6 to 12, and remove Line 18 to use your own details.

Sample Config
config = {
  'host': "localhost",
  'user': "user",
  'password': "password",
  'database': 'db1',
  'raise_on_warnings': True,
}
"""

# Standard Imports
from mysql.connector import connect, errorcode, Error
import pandas as pd
from .privatekeys import config

def get_weatherData():
  """
  API to query data for all available weather data from the database
  Input: None
  Output: Pandas Dataframe
  """
  try:
    cnx = connect(**config)
    cursor = cnx.cursor()
    cursor.execute("select * from weatherHistory")
    records = cursor.fetchall()
    
    df = pd.DataFrame(records)
    df.columns = cursor.column_names
    return df

  except Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
    cnx.close()

def get_weatherData_byCount(n):
  """
  API to query data for last 'n' records from available weather data from the database
  Input: n (Int: count)
  Output: Pandas Dataframe
  """
  try:
    cnx = connect(**config)
    cursor = cnx.cursor()
    cursor.execute("select * from weatherHistory order by id desc limit {}".format(n))
    records = cursor.fetchall()
    
    df = pd.DataFrame(records)
    df.columns = cursor.column_names
    return df

  except Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
    cnx.close()

def get_weatherData_byYear(n):
  """
  API to query data for particular year from available weather data from the database
  Input: n (String: year value)
  Output: Pandas Dataframe
  """
  try:
    cnx = connect(**config)
    cursor = cnx.cursor()
    cursor.execute("select * from weatherHistory where reading_time like '{}%'".format(n))
    records = cursor.fetchall()
    
    df = pd.DataFrame(records)
    df.columns = cursor.column_names
    return df

  except Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
    cnx.close()

def get_weatherData_bySummary(summary):
  """
  API to query all available weather data for defined summary (for eg. Clear, Foggy etc.)
  Input: summary 
  Output: Pandas Dataframe
  """

  try:
    cnx = connect(**config)
    cursor = cnx.cursor()
    cursor.execute("select * from weatherHistory where summary={}".format(summary))
    records = cursor.fetchall()
    
    df = pd.DataFrame(records)
    df.columns = cursor.column_names
    return df

  except Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
    cnx.close()

def add_weatherData(reading_time, summary, precip_type, temperature, apparent_temperature, humidity, wind_speed, wind_bearing, visibility, pressure):
  """
  API to add new weather data to the database
  Input: reading_time, summary, precip_type, temperature, apparent_temperature, humidity, wind_speed, wind_bearing, visibility, pressure
  Output: None
  """
  try:
    cnx = connect(**config)
    cursor = cnx.cursor()
    cursor.execute("INSERT INTO weatherHistory(reading_time, summary, precip_type, temperature, apparent_temperature, humidity, wind_speed, wind_bearing, visibility, pressure) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(reading_time, summary, precip_type, temperature, apparent_temperature, humidity, wind_speed, wind_bearing, visibility, pressure))

  except Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
    cnx.commit()
    cnx.close()
