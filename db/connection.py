# install mysql connector before executing this script using following command
# pip3 install mysql-connector-python
# The connection string is stored in privatekeys.py, uncomment Line 6 to 12, and remove Line 16 to use your own details.

# Sample Config
# config = {
#   'host': "localhost",
#   'user': "user",
#   'password': "password",
#   'database': 'db1',
#   'raise_on_warnings': True,
# }

import mysql.connector
from mysql.connector import errorcode
import pandas as pd
from .privatekeys import config

def get_weatherData():
  """
  Query all available weather data from the database
  Return Type: Pandas Dataframe
  """

  try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("select * from weatherHistory")
    records = cursor.fetchall()
    
    df = pd.DataFrame(records)
    df.columns = cursor.column_names
    return df

  except mysql.connector.Error as err:
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
  Query last 'n' available weather data from the database
  Return Type: Pandas Dataframe
  """

  try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("select * from weatherHistory order by id desc limit {}".format(n))
    records = cursor.fetchall()
    
    df = pd.DataFrame(records)
    df.columns = cursor.column_names
    return df

  except mysql.connector.Error as err:
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
  Query all available weather data for defined summary (for eg. Clear, Foggy etc.)
  Return Type: Pandas Dataframe
  """

  try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("select * from weatherHistory where summary={}".format(summary))
    records = cursor.fetchall()
    
    df = pd.DataFrame(records)
    df.columns = cursor.column_names
    return df

  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
    cnx.close()
