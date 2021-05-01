import time, os, sys
import requests
import datetime
import subprocess

scriptDir = os.path.dirname(__file__)

def faultToleranceTest():

    log = os.path.join(scriptDir, './outputs/faultToleranceTest.txt')
    averageTimeCacheOutput = os.path.join(scriptDir, './outputs/faultToleranceTestOutput.txt')

    local = "http://0.0.0.0:8081/"
    queryList = ["buy/1"]

    # for docker use the following command: "docker rm --force catalog-1"
    process = subprocess.Popen("lsof -i:8082 -t | xargs kill -KILL", shell=True)
    process.wait()

    print("Catalog-1 server is dead now")

    stockValueAfter10Iterations = 0
    for query in queryList:
        totalRequestTime = 0

        for i in range(1):
            requestStart = datetime.datetime.now()
            resp = requests.get(local + query)
            output = open(averageTimeCacheOutput, 'a+')
            output.write(resp.text)
            output.write('\n')
            output.close()
            request_end = datetime.datetime.now()
            requestTime = request_end - requestStart
            stockValueAfter10Iterations = int(resp.json()['res'][0]['stock'])
            totalRequestTime = totalRequestTime + (requestTime.microseconds / 1000)

        print(stockValueAfter10Iterations)

    #wait for the server to spawn
    time.sleep(10)
    #check if the catalog-1 is alive

    resp = requests.get(local)
    if resp.status_code == 200:
        print("The catalog server with port 8082 is up now")    
    else:
        print("The server is not up")
    
    #sleep for the resync operation to complete
    stockValues = 0
    for x in range(10):
        resp = requests.get(local + "lookup/1")
        stockValues = stockValues + int(resp.json()['res'][0]['stock'])

    print(stockValues)

    #the average value of all the values in the stockValues should be equal to the value before the server is dead assuming that now other write operations took place in between

    if stockValueAfter10Iterations == (stockValues/10):
        print("The server respawned and the replicas is perfectly synced up")
    else:
        print("Check if other write operations are performed while the server went dead and got backa alive and resynced")
        


if __name__ == "__main__":
    faultToleranceTest()