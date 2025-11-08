"""
- Class to handle, all kind of data manipulations i.e. resampling, building straddle or spread
"""

## Necessary imports
import pandas as pd


## data manipulation class
class DataManipulatorClass:
    ## Method to resample the dataframe
    def resample_dataframe(self, dataframe:pd.DataFrame, timeframe:str='1min') -> pd.DataFrame:
        resultDf = pd.DataFrame()
        try:
            resultDf = dataframe.resample(timeframe, offset='09:15:00').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last'
            })
        except Exception as e:
            print(f'[resampleDataframe] :: Exception as: {str(e)}')
        resultDf.dropna(inplace=True)
        return resultDf
            
    ## Method to build the zip of OHLC values
    def zip_ohlc_to_list(self, dataframe:pd.DataFrame) -> list:
        ohlcTuples = []
        try:
            ohlcTuples = list(zip(
                dataframe['datetime'],
                dataframe['Open'].astype(float),
                dataframe['High'].astype(float),
                dataframe['Low'].astype(float),
                dataframe['Close'].astype(float)
            ))
        except Exception as e:
            print(f'[zip_ohlc_to_list] :: Exception as: {str(e)}')
        return ohlcTuples

    ## Method to build the straddle ohlc data
    def build_straddle(self, dfCe:pd.DataFrame, dfPe:pd.DataFrame) -> pd.DataFrame:
        resultDf = pd.DataFrame()
        try:
            dfMerged = pd.merge(dfCe, dfPe, how='inner', left_index=True, right_index=True, suffixes=['_call', '_put'])
            resultDf = pd.DataFrame(index=dfMerged.index)
            resultDf['Open'] = dfMerged['Open_call'] + dfMerged['Open_put']
            resultDf['High'] = dfMerged['High_call'] + dfMerged['High_put']
            resultDf['Low']  = dfMerged['Low_call']  + dfMerged['Low_put']
            resultDf['Close'] = dfMerged['Close_call'] + dfMerged['Close_put']
        except Exception as e:
            print(f'[build_straddle] :: Exception as : {str(e)}')
        return resultDf

    ## Method to build the spread OHLC data
    def build_spread(self, dfMain:pd.DataFrame, dfHedge:pd.DataFrame) -> pd.DataFrame:
        resultDf = pd.DataFrame()
        try:
            dfMerged = pd.merge(dfMain, dfHedge, how='inner', left_index=True, right_index=True, suffixes=['_main', '_hedge'])
            resultDf = pd.DataFrame(index=dfMerged.index)
            resultDf['Open'] = dfMerged['Open_main'] - dfMerged['Open_hedge']
            resultDf['High'] = dfMerged['High_main'] - dfMerged['High_hedge']
            resultDf['Low']  = dfMerged['Low_main']  - dfMerged['Low_hedge']
            resultDf['Close'] = dfMerged['Close_main'] - dfMerged['Close_hedge']
        except Exception as e:
            print(f'[build_spread] :: Exception as : {str(e)}')
        return resultDf
