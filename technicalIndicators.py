"""
- Class that holds all the functions related to technical indicators
"""

## Necessary import statements
from abc import ABC, abstractmethod
from collections import deque


## Base class
class TechnicalIndicator(ABC):
    ## Constructor
    def __init__(self):
        pass

    ## Abstract method: To update
    @abstractmethod
    def update(self):
        pass


## Indicator: True Range
class TrueRange(TechnicalIndicator):
    ## Constructor
    def __init__(self):
        super().__init__()

    ## Overriding the upadte method
    def update(self, high, low, closePrev):
        value = 0
        try:
            value = max(
                high - low,
                abs(high - closePrev) if closePrev is not None else 0,
                abs(low - closePrev) if closePrev is not None else 0
            )
        except Exception as e:
            print(f'[update] :: Excception as: {str(e)}')            
        return value


## Indicator: Incremental keltner
class IncrementalKeltner(TechnicalIndicator):
    ## Constructor
    def __init__(self, emaLength:int, atrLength:int, multiplier:float):
        super().__init__()
        self.emaLength = emaLength
        self.atrLength = atrLength
        self.multiplier = multiplier
        self.emaVal = None
        self.atrVal = None
        self.closePrev = None
        self.trQueue = deque(maxlen=self.atrLength)
        self.trueRangeObj = TrueRange()
        self.ema_mult = 2 / (self.emaLength + 1)

    ## Overriding the update method
    def update(self, candle):
        ts, open, high, low, close = candle
        trVal = self.trueRangeObj.update(high, low, self.closePrev)
        ## Initial ATR seed
        if (self.atrVal == None):
            self.trQueue.append(trVal)
            if (len(self.trQueue) < self.atrLength):
                self.closePrev = close
                return None
            self.atrVal = sum(self.trQueue) / self.atrLength
        else:
            self.atrVal = ((self.atrVal * (self.atrLength - 1)) + trVal) / self.atrLength
        ## Calculate keltner values
        if (self.emaVal == None):
            self.emaVal = close
        else:
            self.emaVal = (close - self.emaVal) * self.ema_mult + self.emaVal
        upper = self.emaVal + (self.multiplier * self.atrVal)
        lower = self.emaVal - (self.multiplier * self.atrVal)
        self.closePrev = close
        return round(lower, 2), round(self.emaVal, 2), round(upper, 2)


## Indicator: Incremental SuperTrend (Wilder smoothing)
class IncrementalSupertrend(TechnicalIndicator):
    ## Constructor
    def __init__(self, atrLength:int, multiplier:float):
        super().__init__()
        self.atrLength = atrLength
        self.multiplier = multiplier
        self.atrVal = None
        self.closePrev = None
        self.basic_u = self.basic_l = None
        self.final_u = self.final_l = None
        self.trend = None
        self.currStVal = None
        self.trQueue = deque(maxlen=self.atrLength)
        self.trueRangeObj = TrueRange()        

    ## Overriding the update method
    def update(self, candle):
        ts, open, high, low, close = candle
        trVal = self.trueRangeObj.update(high, low, self.closePrev)
        ## Initial ATR seed
        if (self.atrVal == None):
            self.trQueue.append(trVal)
            if (len(self.trQueue) < self.atrLength):
                self.closePrev = close
                return None
            self.atrVal = sum(self.trQueue) / self.atrLength
        else:
            self.atrVal = ((self.atrVal * (self.atrLength - 1)) + trVal) / self.atrLength
        ## Calculations for supertrend
        hl2 = (high + low) / 2
        self.basic_u = hl2 + (self.multiplier * self.atrVal)
        self.basic_l = hl2 - (self.multiplier * self.atrVal)
        if (self.final_u == None):
            self.final_u = self.basic_u
            self.final_l = self.basic_l
        ## Final upper / lower bands
        self.final_u = (
            self.basic_u if (self.basic_u < self.final_u or self.closePrev > self.final_u) else self.final_u
        )
        self.final_l = (
            self.basic_l if (self.basic_l > self.final_l or self.closePrev < self.final_l) else self.final_l
        )
        ## Determine trend & supertrend value, based on the initial value
        if (self.currStVal == None):
            if(close > self.final_u):
                self.trend = 'up'
                self.currStVal = self.final_l
            else:
                self.trend = 'down'
                self.currStVal = self.final_u
        ## Afterwards, increment it continuosly
        else:
            ## If for the furthur values
            if (self.trend == 'down'):
                if (close > self.final_u):
                    self.trend = 'up'
                    self.currStVal = self.final_l
                else:
                    self.currStVal = self.final_u
            else:
                ## Up-trend continues unless close crosses below lower band
                if (close < self.final_l):
                    self.trend = 'down'
                    self.currStVal = self.final_u
                else:
                    self.currStVal = self.final_l
        ## Set the current close as previous close
        self.closePrev = close
        return (round(self.currStVal, 2), self.trend)
