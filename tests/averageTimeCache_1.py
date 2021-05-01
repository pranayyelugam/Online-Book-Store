import time, os, sys
import requests
import datetime

scriptDir = os.path.dirname(__file__)

def testForCache():

    log = os.path.join(scriptDir, './outputs/averageTimeCache.txt')
    averageTimeCacheOutput = os.path.join(scriptDir, './outputs/averageTimeCacheOutput.txt')

    local = "http://0.0.0.0:8081"
    queryList = ["/lookup/1", "/buy/1", "/search/Distributed Systems"]

    for query in queryList:
        totalRequestTime = 0

        for i in range(1000):
            requestStart = datetime.datetime.now()
            resp = requests.get(local + query)
            output = open(averageTimeCacheOutput, 'a+')
            output.write(resp.text)
            output.write('\n')
            output.close()
            request_end = datetime.datetime.now()
            requestTime = request_end - requestStart
            totalRequestTime = totalRequestTime + (requestTime.microseconds / 1000)
        
        
        averageFile = open(log, 'a+')
        averageFile.write("Average time for {} requests is: {}\n".format( query.split('/')[1],totalRequestTime/1000))
        averageFile.close()



if __name__ == "__main__":
    testForCache()