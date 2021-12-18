import threading
import time

class cacher():
    def __init__(self,maxcachesize,lifetime,loggeri = None)-> dict:
        self.cache = {}
        self.logger = loggeri
        self.maxsize = maxcachesize
        self.Least_Recently_Used={}
        self.cachelifetime = lifetime*1000
        self.lifestime = {}
        self.stop = False
        self.thread = threading.Thread(target=self.__lifetime)
        self.thread.start()
        #return self

    def get(self, key):
        if key in self.cache:
            if self.logger:
                self.logger.debug(f"Getting Value From Key {key}")
            self.Least_Recently_Used[key] = int(time.time())
            return self.cache[key]
        else:
            return None

    def set(self, key, value):
        self.lifestime[key] = time.time()+self.cachelifetime
        if self.logger:
            self.logger.debug(f"Set Value With Key {key}")
        if len(self.cache.keys()) > self.maxsize:
            self.__clean_lru()
        self.cache[key] = value

    def clear_cache(self):
        self.cache = {}
        self.lifestime = {}
        self.Least_Recently_Used = {}
        if self.logger:
            self.logger.debug("Clear Cache")

    def __clean_lru(self):
        leastusedtime = 0
        leastusedkey = ""
        for key,recently_used in self.Least_Recently_Used:
            if leastusedtime > recently_used - int(time.time()):
                leastusedtime = int(time.time())
                leastusedkey = key
        self.Least_Recently_Used[leastusedkey] = None
        self.cache[leastusedkey] = None
        self.lifestime[leastusedkey] = None

    def __lifetime(self):
        while not self.stop:
            if len(self.cache.keys()) > 0:
                for key in self.lifestime:
                    if time.time() >= self.lifestime[key]:
                        self.cache[key] = None
                        self.lifestime[key] = None
                        self.Least_Recently_Used[key] = None
            time.sleep(1/10)
