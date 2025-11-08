"""
- Class to handle the logs of the executed trades: either paper trade or live trade
"""

## Necessary import Statements
import pandas as pd

## Logger class
class TradeLogger:
    ## Constructor
    def __init__(self, savingFilepath:str):
        self.logs_list = []
        self.savingFilepath = savingFilepath

    ## To log or store the trade
    def log_trade(self, strategy_name, entry_datetime, trading_symbol, trade_entry_price, exit_datetime, trade_exit_price, booked_qty, profit_amount, exit_reason, extra_info=None):
        log = {
            "Strategy_name": strategy_name,
            "Entry_datetime": entry_datetime,
            "Trading_symbol": trading_symbol,
            "Entry_price": trade_entry_price,
            "Exit_datetime": exit_datetime,
            "Exit_price": trade_exit_price,
            "Booked_qty": booked_qty,
            "Profit_rs": profit_amount,
            "Exit_reason": exit_reason
        }
        if extra_info:
            log.update(extra_info)
        self.logs_list.append(log)

    ## Method to write all collected trades to CSV once (at shutdown).
    def save_to_csv(self) -> bool:
        status = False
        if (not self.logs_list):
            print(f'[save_to_csv] :: No trades logged, nothing to save.')
        else:
            df = pd.DataFrame(self.logs_list)
            df.to_csv(self.savingFilepath)
            status = True
            print(f'[save_to_csv] :: Trade logs saved to {self.savingFilepath}')
        return status
