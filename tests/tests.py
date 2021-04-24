import json, requests, os, time, sys

scriptDir = os.path.dirname(__file__)
outputPath = 'tests.txt'
outputPath = os.path.join(scriptDir, outputPath)

def callTests(frontendUri):

        with open(outputPath, 'w') as f:
            f.write("######################### SEARCH TESTCASES FRONTEND SERVER ########################################\n")
            f.write('\n')
            res = requests.get(frontendUri + '/search/Distributed Systems')
            f.write("TEST CASE 1 ---  Request should return 2 items with Distributed Systems as topic\n")
            f.write('\n')
            f.write('=========================================================================\n')
            f.write("REQUEST: /search/Distributed Systems  (search for topic: Distributed Systems)\n")
            f.write("EXPECTED RESPONSE: 2 Items with topic distributed systems \n")
            f.write('=========================================================================\n')

            count = 0
            for item in res.json()['res']:
                if item['topic'] == "Distributed Systems":
                    count = count + 1
            
            if count == 3:
                f.write("Test Case 1 Passed\n")
            else:
                f.write("Test Case 1 Failed\n")
            f.write("Response for the request\n")          
            f.write(res.text)
            f.write('\n')

            f.write("################################### LOOKUP TESTCASES FRONTEND SERVER #################################\n")
            f.write('\n')
            f.write("TEST CASE 2 ---  Request should return 1 items which has item number 1\n")
            f.write('\n')
            res = requests.get(frontendUri + '/lookup/1')
            f.write('=======================================================================\n')
            f.write("REQUEST: /lookup/1 (search for item: 1)\n")
            f.write("EXPECTED RESPONSE: 1 item with itemNumber 1 \n")
            f.write('========================================================================\n')


            count = 0
            for item in res.json()['res']:
                if item['itemNumber'] == "1":
                    count = count + 1
            
            if count == 1:
                f.write("Test Case 2 Passed\n")
            else:
                f.write("Test Case 2 Failed\n")
            f.write("Response for the request\n")
            f.write(res.text)

            f.write('\n')
            f.write("################################## BUY TESTCASES FRONTEND  SERVER #################################\n")
            f.write('\n')
            f.write("TEST CASE 3 ---  Server should return the updated item with the updated stock  \n")
            f.write('========================================================================\n')
            f.write('\n')
            f.write("REQUEST: /buy/1 (Initiated buy request for item: 1)\n")
            lookup = requests.get(frontendUri + '/lookup/1')
            lookupJson = lookup.json()
            initialStock =  int(lookupJson['res'][0]['stock'])
            f.write("Intital stock of the item number 1 is %d\n" % initialStock)
            res = requests.get(frontendUri + '/buy/1')
            expectedStockValue = initialStock - 1

            if expectedStockValue == int(res.json()['res'][0]['stock']):
                f.write("Test Case 3 passed\n")
            else:
                f.write("Test Case 3 Failed\n")
            f.write("Response for the request\n")
            f.write(res.text)
            f.write('\n')
        
            f.write("################################### UPDATECOST TESTCASES CATALOG SERVER #################################\n")
            f.write('\n')
            f.write("TEST CASE 4 ---  Update the cost of the item correctly 1\n")
            f.write('\n')
            res = requests.get(catalogUri + '/updateCost/1/25')
            f.write('=======================================================================\n')
            f.write("REQUEST: /updateCost/1/25 (update cost of the item: 1)\n")
            f.write("EXPECTED RESPONSE: updated cost with 25 \n")
            f.write('========================================================================\n')


            count = 0
            for item in res.json():
                if item['cost'] == "25":
                    count = count + 1
            
            if count == 1:
                f.write("Test Case 4 Passed\n")
            else:
                f.write("Test Case 4 Failed\n")
            f.write("Response for the request\n")
            f.write(res.text)
            f.write('\n')

            f.write("################################### UPDATESTOCK TESTCASES CATALOG SERVER #################################\n")
            f.write('\n')
            f.write("TEST CASE 5 ---  Update the stock of the item correctly 1\n")
            f.write('\n')
            res = requests.get(catalogUri + '/updateStock/1/25')
            f.write('=======================================================================\n')
            f.write("REQUEST: /updateStock/1/25 (update stock of the item: 1)\n")
            f.write("EXPECTED RESPONSE: updated stock with 25 \n")
            f.write('========================================================================\n')


            count = 0
            for item in res.json():
                if item['stock'] == "25":
                    count = count + 1
            
            if count == 1:
                f.write("Test Case 5 Passed\n")
            else:
                f.write("Test Case 5 Failed\n")
            f.write("Response for the request\n")
            f.write(res.text)
            f.write('\n')

if __name__ == "__main__":
    frontendUri = sys.argv[1]
    catalogUri = sys.argv[2]
    callTests(frontendUri)
