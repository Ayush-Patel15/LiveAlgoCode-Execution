"""
- Class to build the OHLC of the candle: for the specified timeframe
"""

## Necessary imports
import datetime
import math


## Base Class
class LiveCandleBuilder:
    ## Constructor
    def __init__(self, intervalInSec:int=60):
        self.intervalInSec = intervalInSec
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.currT0 = None
        self.lastCandle = None

    ## Return timestamp floored to the interval start
    def floor_ts(self, ts:datetime.datetime):
        epoch = ts.timestamp()
        floored = math.floor(epoch / self.intervalInSec) * self.intervalInSec
        flooredDt = datetime.datetime.fromtimestamp(floored)
        return flooredDt
    
    ## Method to update candle: based on the ltp passed to it
    def update_candle(self, ts:datetime.datetime, ltp:float):
        ts = ts.replace(microsecond=0)
        winStart = self.floor_ts(ts)
        ## First tick of the first candle
        if (self.currT0 == None):
            self.currT0 = winStart
            self.open = self.high = self.low = self.close = ltp
            return None
        ## New candle formed
        if (winStart > self.currT0):
            self.lastCandle = (self.currT0, self.open, self.high, self.low, self.close)
            self.currT0 = winStart
            self.open = self.high = self.low = self.close = ltp
        ## Still within current candle
        else:
            self.high = max(self.high, ltp)
            self.low = min(self.low, ltp)
            self.close = ltp
        return self.lastCandle

    ## Method: of update - to be implemented in subclasses
    def update(self, ts:datetime.datetime, ltp:float):
        return self.update_candle(ts, ltp)


## Straddle Candle Builder
class StraddleCandleBuilder(LiveCandleBuilder):
    ## Constructor
    def __init__(self, intervalInSec:int=60):
        super().__init__(intervalInSec)

    ## Method overriding i.e. the update fuction
    def update(self, ts:datetime.datetime, ceLtp:float, peLtp:float):
        if(ceLtp == None or peLtp == None):
            return self.lastCandle
        straddleLtp = round(ceLtp + peLtp, 2)
        return self.update_candle(ts, straddleLtp)


## Spread Candle Builder
class SpreadCandleBuilder(LiveCandleBuilder):
    ## Constructor
    def __init__(self, intervalInSec:int=60):
        super().__init__(intervalInSec)

    ## Method overriding i.e. the update fuction
    def update(self, ts:datetime.datetime, buyLtp:float, sellLtp:float):
        if(buyLtp == None or sellLtp == None):
            return self.lastCandle
        spreadLtp = round(buyLtp - sellLtp, 2)
        return self.update_candle(ts, spreadLtp)
