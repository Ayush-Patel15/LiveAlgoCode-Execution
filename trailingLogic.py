"""
- Class to trail exit the lots, under a strategy --> based on ther points earned
"""

## Necessary imports
from abc import ABC, abstractmethod


## Base Trail Class
class TrailExitOnPoints(ABC):
    ## Constructor
    def __init__(self, totalLots:int, startPrice:float, trailingPoints:float):
        self.totalLots = totalLots
        self.startPrice = startPrice
        self.trailingPoints = trailingPoints
        self.lotsExited = 0
    
    ## Abstract method: to get trailing levels
    @abstractmethod
    def get_trailing_levels(self):
        pass

    ## Abstract method: to check the trailing exit
    @abstractmethod
    def check_trailing_exit(self, ltp:float):
        pass


## Short Trade trailing class
class ShortTradeTrailing(TrailExitOnPoints):
    ## Constructor
    def __init__(self, totalLots:int, startPrice:float, trailingPoints:float):
        super().__init__(totalLots, startPrice, trailingPoints)
        self.exitLevels = self.get_trailing_levels()
        self.length = len(self.exitLevels)

    ## Overriding of abstract class
    def get_trailing_levels(self) -> list:
        return [round(self.startPrice - (i * self.trailingPoints), 2) for i in range(1, self.totalLots)]
    
    ## Overriding of abstract class
    def check_trailing_exit(self, ltp:float) -> bool:
        status = False
        if(self.lotsExited < self.length):
            if(ltp <= self.exitLevels[self.lotsExited]):
                self.lotsExited += 1
                status = True
        return status

    ## Method to check, whether all lots are exited or not
    def all_lots_exited(self) -> bool:
        return self.lotsExited >= self.length
    

## Long Trade trailing class
class LongTradeTrailing(TrailExitOnPoints):
    ## Constructor
    def __init__(self, totalLots:int, startPrice:float, trailingPoints:float):
        super().__init__(totalLots, startPrice, trailingPoints)
        self.exitLevels = self.get_trailing_levels()
        self.length = len(self.exitLevels)

    ## Overriding of abstract class
    def get_trailing_levels(self) -> list:
        return [round(self.startPrice + (i * self.trailingPoints), 2) for i in range(1, self.totalLots)]
    
    ## Overriding of abstract class
    def check_trailing_exit(self, ltp:float) -> bool:
        status = False
        if(self.lotsExited < self.length):
            if(ltp >= self.exitLevels[self.lotsExited]):
                self.lotsExited += 1
                status = True
        return status

    ## Method to check, whether all lots are exited or not
    def all_lots_exited(self) -> bool:
        return self.lotsExited >= self.length
