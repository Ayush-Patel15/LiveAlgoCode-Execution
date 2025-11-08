"""
- Class to call the place order function using the XTS
"""

## Necessary import statements
from auth import XTSClient
from typing import Literal
import constants as ct


## Base Place order Class
class PlaceOrder(XTSClient):
    ## Constructor
    def __init__(self, orderIdentifier:str, needAuth:bool=True):
        super().__init__(needAuth)
        self.orderIdentifier = orderIdentifier
        self.response = {}

    ## Method to place market order
    def place_market_order(self, exchangeSegment, productType, timeInForce, exchangeInstrumentID, numberOfLots, lotSize, orderSide) -> dict:
        self.response = self.xtsObj.place_order(
            exchangeSegment=exchangeSegment,
            productType=productType,
            orderType=self.xtsObj.ORDER_TYPE_MARKET,
            timeInForce=timeInForce,
            exchangeInstrumentID=exchangeInstrumentID,
            orderQuantity=(numberOfLots * lotSize),
            orderSide=orderSide,
            disclosedQuantity=0,
            limitPrice=0,
            stopPrice=0,
            apiOrderSource="AlgoOrder",
            orderUniqueIdentifier=self.orderIdentifier,
            clientID=ct.CLIENT_ID
        )
        return self.response

    ## Method to place limit order
    def place_limit_order(self, exchangeSegment, productType, timeInForce, exchangeInstrumentID, numberOfLots, lotSize, orderSide, limitPrice, stopPrice)  -> dict:
        self.response = self.xtsObj.place_order(
            exchangeSegment=exchangeSegment,
            productType=productType,
            orderType=self.xtsObj.ORDER_TYPE_LIMIT,
            timeInForce=timeInForce,
            exchangeInstrumentID=exchangeInstrumentID,
            orderQuantity=(numberOfLots * lotSize),
            orderSide=orderSide,
            disclosedQuantity=0,
            limitPrice=limitPrice,
            stopPrice=stopPrice,
            apiOrderSource="AlgoOrder",
            orderUniqueIdentifier=self.orderIdentifier,
            clientID=ct.CLIENT_ID
        )
        return self.response

    ## Paper trade: Demo response
    def get_paper_trade_response(self) -> dict:
        self.response = {
            'type': 'success',
            'result': {
                'AppOrderID': 1000000,
                'orderUniqueIdentifier': self.orderIdentifier
            }
        }
        return self.response


## Order Placement Class
class OrderPlacementClass(PlaceOrder):
    ## Constructor
    def __init__(self, orderIdentifier:str, deploymentType:str='paper', needAuth:bool=True):
        super().__init__(orderIdentifier, needAuth)
        self.deploymentType = deploymentType

    ## Method to place a MIS market order
    def fo_mis_market_order(self, transactionType:Literal['buy','sell'], exchangeInstrumentID:int, lotSize:int, numberOfLots:int, strikeToTrade:str='0') -> dict:
        response = {}
        orderSide = self.xtsObj.TRANSACTION_TYPE_BUY if(transactionType=='buy') else self.xtsObj.TRANSACTION_TYPE_SELL
        if(self.deploymentType == 'live'):
            response = self.place_market_order(
                exchangeSegment=self.xtsObj.EXCHANGE_NSEFO,
                productType=self.xtsObj.PRODUCT_MIS,
                timeInForce=self.xtsObj.VALIDITY_DAY,
                exchangeInstrumentID=exchangeInstrumentID,
                numberOfLots=numberOfLots,
                lotSize=lotSize,
                orderSide=orderSide
            )
        elif (self.deploymentType == 'paper'):
            response = self.get_paper_trade_response()
        print(f'[fo_mis_market_order] :: {self.deploymentType} ==> {strikeToTrade} @ {numberOfLots},{lotSize} :: ', response, '\n')
        return response

    ## Method to place a CNC market order
    def fo_cnc_market_order(self, transactionType:Literal['buy','sell'], exchangeInstrumentID:int, lotSize:int, numberOfLots:int, strikeToTrade:str='0') -> dict:
        response = {}
        orderSide = self.xtsObj.TRANSACTION_TYPE_BUY if(transactionType=='buy') else self.xtsObj.TRANSACTION_TYPE_SELL
        if(self.deploymentType == 'live'):
            response = self.place_market_order(
                exchangeSegment=self.xtsObj.EXCHANGE_NSEFO,
                productType=self.xtsObj.PRODUCT_NRML,
                timeInForce=self.xtsObj.VALIDITY_DAY,
                exchangeInstrumentID=exchangeInstrumentID,
                numberOfLots=numberOfLots,
                lotSize=lotSize,
                orderSide=orderSide
            )
        elif (self.deploymentType == 'paper'):
            response = self.get_paper_trade_response()
        print(f'[fo_cnc_market_order] :: {self.deploymentType} ==> {strikeToTrade} @ {numberOfLots},{lotSize} :: ', response, '\n')
        return response
