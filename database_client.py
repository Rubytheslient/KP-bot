import time
import redis
import logging
from Caching import cacher
class database_client():
    
    def __init__(self, hostip:str='localhost', hostport:int=6379, databasenum:int=0,loggeri = None):
        self.redisclient = redis.Redis(host=hostip, port=hostport, db=databasenum)
        self.cache = cacher(2,600)
        self.logger = loggeri

    def get(self, key:str, force:bool=False, caching:bool = True) -> bytes:
        try:
            self.logger.debug(f"get value from database {key}")
            if key:
                data = self.cache.get(key)
                if data and not force:
                    return data
                data = self.redisclient.get(key)
                if caching:
                    self.cache.set(key,data)
                return data
        except:
            return 0x00
            
    def set(self, key, value) -> bool:
        success = False
        retries = 5
        exception = ""
        while retries > 0:
            try:
                self.redisclient.set(key,value)
                success = True
                break
            except Exception as e:
                retries -= 1
                logging.error(e)
                exception = e
                time.sleep()
        return success, exception
        