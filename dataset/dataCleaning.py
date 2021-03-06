import pandas as pd
import numpy as np

def cleanData(df):
    """
    API to take pandas dataframe as argument, perform standard cleaning as per research done earlier
    1. Convert Formatted Date column to datetime format for easier manipulation
    2. Replace Null values in Precip Type to string value "none"

    Input: df (Pandas DataFrame)
    Output: Pandas DataFrame
    """
    df['reading_time'] = pd.to_datetime(df['reading_time'], utc=True)
    df['precip_type'] = df['precip_type'].replace(np.nan, "none")

    return df
