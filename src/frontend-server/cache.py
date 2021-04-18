import os, time, sys
import threading

class Cache():

    def __init__(self, cacheSize=4):
        self.cache = {}
        self.lock = threading.Lock()
        self.cacheSize = 4
    
    def put(self, key, value):
        with self.lock:
            if key not in self.cache:
                print("adding to cache")
                self.cache[key] = value
            return key
        
    def get(self, key):
        with self.lock:
            if key in self.cache:
                print("getting from cache")
                return self.cache[key]
            else:
                return "not found"
        
    def erase(self, key):
        with self.lock:
            if key in self.cache:
                print("removing element from cache", key)
                del self.cache[key]
            return