"""
- Class to build and maintain the websocket
"""

## Necessary imports
from helpers import Helper5Paisa
from redisDB import RedisClass
from auth import Broker5Paisa
import constants as ct
import pandas as pd
import threading
import datetime
import ujson
import queue
import pytz
import time


## Base class of Websocket
class WebSocketBase(Broker5Paisa):
    ## Constructor
    def __init__(self, needAuth:bool=True):
        super().__init__(needAuth)

    ## Method to subscribe for instruments
    def ws_subscribe(self, subscriptionList:list) -> list:
        subsResponse = []
        try:
            subsResponse = self.brokerObj.Request_Feed(ct.WS_MARKET_FEED, ct.WS_SUBSCRIBE, subscriptionList)
        except Exception as e:
            print(f'[ws_subscribe] :: Exception as: {str(e)}')
        return subsResponse
    
    ## Method to unsubscribe for instruments
    def ws_unsubscribe(self, unsubscriptionList:list) -> list:
        unsubsResponse = []
        try:
            unsubsResponse = self.brokerObj.Request_Feed(ct.WS_MARKET_FEED, ct.WS_UNSUBSCRIBE, unsubscriptionList)
        except Exception as e:
            print(f'[ws_unsubscribe] :: Exception as: {str(e)}')
        return unsubsResponse

    ## Method to close the connection
    def ws_close(self):
        try:
            self.brokerObj.close_data()
            print(f'[ws_close] :: Successfully closed the connection')
        except Exception as e:
            print(f'[ws_close] :: Exception as: {str(e)}')



## Websocket class to write or run
class WebSocketWriter(WebSocketBase):
    ## Constructor
    def __init__(self, rdb:RedisClass, criticalScrips:set, queueSize:int, needAuth:bool=True):
        super().__init__(needAuth)
        self.IST = pytz.timezone('Asia/Kolkata')
        self.rdb = rdb
        self.criticalScrips = criticalScrips
        self.tickQueue = queue.Queue(maxsize=queueSize)
        self.lastTickTime = time.time()
        self.batchSize = 25
        self.batchTimeout = 0.02  # 20ms
        self.tickCount = 0

    ## Return 'ltp,timestamp' with millisecond ISO, eg '452.3,2025-06-17T12:34:56.123'
    def encode_tick(self, ltp:float) -> str:
        ts = datetime.datetime.now(self.IST)
        encoded = f"{ltp},{ts.isoformat(timespec='milliseconds')}"
        return encoded

    ## Method to perform on tick
    def on_tick(self, messages:str):
        try:
            if(messages):
                jsonMsgsList = ujson.loads(messages)
                for msg in jsonMsgsList:
                    scripCode = msg.get('Token')
                    scripLtp = msg.get('LastRate')
                    if ((scripCode) and (scripLtp)):
                        try:
                            if (scripCode in self.criticalScrips):
                                self.rdb.conn.set(f'tick:{scripCode}', self.encode_tick(scripLtp))
                            else:
                                self.tickQueue.put_nowait((scripCode, scripLtp))
                                self.tickCount += 1
                        except queue.Full:
                            print(f'[on_tick] :: Queue is full, dropping tick')
                ## Periodic logging instead of per-tick and update the last time
                self.lastTickTime = time.time()
                if (self.tickCount % 100 == 0):
                    print(f'[on_tick] :: Processed {self.tickCount} ticks')
                    self.tickCount  = 0
            else:
                print(f'[on_tick] ::  No Data in websocket: {messages}, {len(messages)}')
        except Exception as e:
            print(f'[on_tick] :: Exception as: {str(e)}')


    ## Method to batch write in redis
    def batch_write(self):
        batchData = {}
        lastBatchTime = time.time()
        while True:
            try:
                scripCode, scripLtp = self.tickQueue.get(timeout=self.batchTimeout)
                batchData[f'tick:{scripCode}'] = self.encode_tick(scripLtp)
                ## Process batch if size reached or timeout exceeded
                currentTime = time.time()
                if (len(batchData) >= self.batchSize) or (batchData and (currentTime - lastBatchTime > self.batchTimeout)):
                    self.rdb.conn.mset(batchData)
                    batchData.clear()
                    lastBatchTime = currentTime
            except Exception as e:
                ## Timeout reached, process any pending data
                if (batchData):
                    self.rdb.conn.mset(batchData)
                    batchData.clear()
                    lastBatchTime = time.time()
                print(f'[batch_write] :: Exception as: {str(e)}')
                time.sleep(0.005)


    ## Method to connect to the websocket
    def receiver(self, subsResponse):
        retry_count = 0
        while True:
            try:
                print("[receiver] Connecting WebSocket...")
                self.brokerObj.connect(subsResponse)
                print("[receiver] Starting to receive data...")
                self.brokerObj.receive_data(self.on_tick)
                retry_count = 0
            except Exception as e:
                print(f"[receiver] WebSocket failed: {e}")
                retry_count += 1
                if retry_count > 5:
                    print("[receiver] Max retries exceeded, giving up.")
                    self.ws_close()
                    self.play_beep_sound()
                    return
                print(f"[receiver] Retrying in 100 milliseconds... (Attempt {retry_count})")
                time.sleep(0.1)

    ## Function to run the webscocket
    def run(self, subsResponse):
        self.lastTickTime = time.time()
        ## Initialize threads
        batchWriteThread = threading.Thread(target=self.batch_write, daemon=True)
        dataThread = threading.Thread(target=self.receiver, args=(subsResponse,), daemon=True)
        monitorThread = threading.Thread(target=self.monitor, args=(30,), daemon=True)
        ## Start the threads
        batchWriteThread.start()
        dataThread.start()
        monitorThread.start()
        print(f"[run] :: WebSocket connection established for processing..")
        ## Keep main thread alive
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("[run] :: Shutting down WebSocket client...")
            self.ws_close()

    ## Method to monitor the working of websocket
    def monitor(self, timeout):
        while True:
            if (time.time() - self.lastTickTime > timeout):
                print(f"[WATCHDOG WARNING] No tick received in last {timeout} seconds.")
                self.play_beep_sound()
            time.sleep(1)

    ## Method to play a beep sound to alert the user
    def play_beep_sound(self):
        try:
            print('\a')
            print('Beep alert played')
        except Exception as e:
            print(f'[play_beep_sound] :: Exception as: {str(e)}')


## Websocket setup to run
class WebSocketSetup:
    ## Constructor
    def __init__(self, rdb:RedisClass, instrumentName:str, spotScripCode:int, expiryDate:str, strikeJump:int=50, strikeRange:int=10):
        self.brokerInstFoPath = 'Instruments/ScripMaster_nse_fo.csv'
        self.instrumentName = instrumentName
        self.spotScripCode = spotScripCode
        self.expiryDate = expiryDate
        self.strikeJump = strikeJump
        self.strikeRange = strikeRange
        self.criticalScrips = set()
        self.subscriptionList = []
        self.todaysATMStrike = int(input('Middle ATM strike, to start from: '))
        self.helper= Helper5Paisa()
        self.rdb = rdb

    ## Method to setup the required fields
    def create_setup(self):
        self.criticalScrips.add(self.spotScripCode)
        self.subscriptionList.append({'Exch': ct.EXCHANGE_NSE, 'ExchType': ct.PRODUCT_TYPE_CASH, 'ScripCode': self.spotScripCode})
        brokerDf = pd.read_csv(self.brokerInstFoPath)
        ## Iterate to populate the list
        for i in range(-self.strikeRange, self.strikeRange+1):
            currStrike = self.todaysATMStrike + (i * self.strikeJump)
            ceToken = self.helper.get_5paisa_scrip_code(brokerDf, ct.EXCHANGE_NSE, ct.PRODUCT_TYPE_DERIVATIVE, self.instrumentName, ct.SCRIPT_TYPE_CALL, currStrike, self.expiryDate)
            peToken = self.helper.get_5paisa_scrip_code(brokerDf, ct.EXCHANGE_NSE, ct.PRODUCT_TYPE_DERIVATIVE, self.instrumentName, ct.SCRIPT_TYPE_PUT, currStrike, self.expiryDate)
            self.subscriptionList.append({'Exch': ct.EXCHANGE_NSE,'ExchType': ct.PRODUCT_TYPE_DERIVATIVE,'ScripCode': ceToken})
            self.subscriptionList.append({'Exch': ct.EXCHANGE_NSE,'ExchType': ct.PRODUCT_TYPE_DERIVATIVE,'ScripCode': peToken})
            ## For ATM and -100 and +100 tokens
            if(i >= -2 and i <= 2):
                self.criticalScrips.add(ceToken)
                self.criticalScrips.add(peToken)
            ## Write or set in redis
            self.rdb.conn.set(f'{currStrike}{ct.SCRIPT_TYPE_CALL}', ceToken)
            self.rdb.conn.set(f'{currStrike}{ct.SCRIPT_TYPE_PUT}', peToken)
            print(f'{currStrike}{ct.SCRIPT_TYPE_CALL} :: {ceToken} | {currStrike}{ct.SCRIPT_TYPE_PUT} :: {peToken}')


## ___main__ function
if __name__ == '__main__': 
    ## Create objects and run the websocket
    rdb = RedisClass(host='localhost', port=6379)
    if (rdb.check_connection()):
        wsSetupObj = WebSocketSetup(rdb, ct.NIFTY_INSTRUMENT_NAME, ct.NIFTY_SPOT_SCRIP_CODE, ct.CURR_M_EXPIRY_DATE, strikeJump=50, strikeRange=10)
        wsSetupObj.create_setup()
        print('Created subscription list:', wsSetupObj.subscriptionList, '\n')
        print('Priority Scrip codes are:', wsSetupObj.criticalScrips, '\n')

        ## WebSocket writer object
        wsWriterObj = WebSocketWriter(rdb, wsSetupObj.criticalScrips, queueSize=3000, needAuth=False)
        subsResponse = wsWriterObj.ws_subscribe(wsSetupObj.subscriptionList)
        if(subsResponse):
            wsWriterObj.run(subsResponse)
        else:
            print('[ERROR] :: Websocket connections are not done properly, Do not run the algo.. !!')
            wsWriterObj.play_beep_sound()
    else:
        print('Redis not connected, stopping the websocket.... !!')
