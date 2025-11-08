"""
- Class to consist of all Redis Functionalities
"""

## Necessary imports
import datetime
import redis


## Base Redis class
class RedisClass:
    ## Constructor 
    def __init__(self, host:str='localhost', port:int=6379):
        redisPool = redis.ConnectionPool(host=host, port=port, db=0, max_connections=10)
        self.conn = redis.Redis(connection_pool=redisPool)

    ## Method to check the redis connection
    def check_connection(self) -> bool:
        status = False
        try:
            self.conn.ping()
            status = True
        except Exception as e:
            print(f'[check_connection] :: Exception as: {str(e)}')
        return status

    ## Method to get the token, from redis
    def get_token(self, strike:str) -> int:
        token = 0
        try:
            raw = self.conn.get(f'{strike}')
            if(raw):
                rawToken = raw.decode()
                token = int(rawToken)
        except Exception as e:
            print(f'[get_token] :: Exception as: {str(e)}')
        return token

    ## Method to get the ltp
    def get_ltp(self, token:int) -> float:
        ltp = 0.0
        try:
            raw = self.conn.get(f'tick:{token}')
            if(raw):
                ltpStr = raw.decode().split(',')[0]
                ltp = float(ltpStr)
        except Exception as e:
            print(f'[get_ltp] :: Exception as: {str(e)}')
        return ltp

    ## Method to get ltp and time both
    def get_ltp_time(self, token:int) -> list:
        result = [0, 0]
        try:
            raw = self.conn.get(f'tick:{token}')
            ltpStr, tsStr = raw.decode().split(',')
            result[0] = float(ltpStr)
            result[1] = datetime.datetime.fromisoformat(tsStr)
        except Exception as e:
            print(f'[decode] :: Exception as: {str(e)}')
        return result
