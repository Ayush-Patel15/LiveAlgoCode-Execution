"""
Consist of all the helper class function, required for the strategy and execution
"""

## Necessary imports
from auth import XTSClient
import constants as ct
import pandas as pd


## Helper Class of XTS
class HelperXts(XTSClient):
    ## Constructor
    def __init__(self, needAuth:bool=True):
        super().__init__(needAuth)

    ## Method to get the order executed price: from order history
    def get_execution_price_from_order_history(self, orderId:int) -> float:
        orderPrice = 0.0
        orderResponse = self.xtsObj.get_order_history(orderId, ct.CLIENT_ID)
        if(orderResponse['type'] == 'success'):
            for ordJson in orderResponse['result']:
                if (ordJson['OrderStatus'] == 'Filled' or ordJson['OrderStatus'] == 'PartiallyFilled'):
                    orderPrice = float(ordJson['OrderPrice'])       ## Or OrderAverageTradedPrice
        return orderPrice


## Helper Class of 5Paisa
class Helper5Paisa:
    ## Constructor
    def __init__(self):
        pass

    ## Method to get the 5 paisa scrip code: Returns Scrip Code or None
    def get_5paisa_scrip_code(self, dataframe:pd.DataFrame, exchange:str, ExchType:str, instName:str, ScripType:str, strike:int, expiry:str='') -> int:
        scripCode = 0
        try:
            scripCode = dataframe[
                (dataframe['Exch']==exchange) & 
                (dataframe['ExchType']==ExchType) & 
                (dataframe['SymbolRoot']==instName) &
                (dataframe['ScripType']==ScripType) & 
                (dataframe['StrikeRate']==strike) & 
                (dataframe['Expiry']==expiry)].iloc[0]['ScripCode']
        except Exception as e:
            print(f'[get_5paisa_scrip_code] :: Exception as: {str(e)}')
        return int(scripCode)




