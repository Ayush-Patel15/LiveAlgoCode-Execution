"""
- Class to fetch the historical data of any required instrument: using the 5Paisa client
"""

## Necessary imports
from auth import Broker5Paisa
import pandas as pd
import datetime


## Historical Data Class
class HistoricalDataClass(Broker5Paisa):

    ## Constructor
    def __init__(self, needAuth:bool=True):
        super().__init__(needAuth)

    ## Method to fetch the historical data of options
    def fetch(self, exchange:str, ExchangeSegment:str, scripCode:int) -> pd.DataFrame:
        dataframe = pd.DataFrame()
        endDt = datetime.datetime.now()
        startDt = endDt - datetime.timedelta(days=7)
        try:
            startDt = str(startDt.strftime('%Y-%m-%d'))
            endDt = str(endDt.strftime('%Y-%m-%d'))
            dataframe = self.brokerObj.historical_data(
                Exch=exchange,
                ExchangeSegment=ExchangeSegment,
                ScripCode=scripCode,
                time='1m',      ## 1 minute always
                From=startDt,
                To=endDt       
            )
            dataframe['datetime'] = pd.to_datetime(dataframe['Datetime'])
            ## Drop duplicates, sort
            dataframe = dataframe.drop_duplicates(subset='datetime').sort_values('datetime')
            dataframe.set_index('datetime', inplace=True)
        except Exception as e:
            print(f"[fetch] ERROR: {e}")
        return dataframe
