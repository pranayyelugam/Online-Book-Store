import time, os, sys
import requests
import datetime

scriptDir = os.path.dirname(__file__)

def testForCacheMiss():

    log = os.path.join(scriptDir, './outputs/averageTimeCacheMiss.txt')
    averageTimeCacheOutput = os.path.join(scriptDir, './outputs/averageTimeCacheMissOutput.txt')

    local = "http://0.0.0.0:8081"
    queryList = ["/lookup/1", "/lookup/1", "/buy/1", "/lookup/1", "/search/Distributed Systems", "/search/Distributed Systems", "/buy/1", "/search/Distributed Systems"]

    for query in queryList:
        totalRequestTime = 0

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
        averageFile.write("Average time for {} requests is: {}\n".format( query.split('/')[1],totalRequestTime))
        averageFile.close()



if __name__ == "__main__":
    testForCacheMiss()