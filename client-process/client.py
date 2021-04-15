import requests, json, os, time, sys

scriptDir = os.path.dirname(__file__)
outputPath = 'ClientOutput.txt'
outputPath = os.path.join(scriptDir, outputPath)

def callApiRequests(frontendUri):

    with open(outputPath, 'w') as f:
        f.write("==================================== Search ======================================\n")

        res = requests.get(frontendUri + '/search/Distributed Systems')
        f.write("REQUEST: /search/Distributed Systems  (search for topic: Distributed Systems)\n")
        f.write("RESPONSE: The books found for the topic Distributed Systems are ....... \n")
        f.write(res.text)

        res = requests.get(frontendUri + '/search/Graduate School')
        f.write("REQUEST: /search/Graduate School (search for topic: Graduate School)\n")
        f.write("RESPONSE: The books found for the topic Graduate School are ....... \n")
        f.write(res.text)

        f.write("================================== Lookup ================================\n")

        res = requests.get(frontendUri + '/lookup/1')
        f.write("REQUEST: /lookup/1 (search for item: 1)\n")
        f.write("RESPONSE: The books found for the item number 1 are....... \n")
        f.write(res.text)

        res = requests.get(frontendUri + '/lookup/3')
        f.write("REQUEST: /lookup/3  (search for item: 3)\n")
        f.write("RESPONSE: The books found for the item number 3 are....... \n")
        f.write(res.text)

        f.write("================================== Buy ================================\n")

        res = requests.get(frontendUri + '/buy/1')
        f.write("REQUEST: /buy/1 (Initiated buy request for item: 1)\n")
        if len(res.json()['res']) > 0:
            f.write("RESPONSE: Bought book %s\n" % res.json()['res'][0]['title'])
        else:
            f.write("RESPONSE: %s\n" % res.json()['msg'])

        res = requests.get(frontendUri + '/buy/3')
        f.write("REQUEST: /buy/3 (Initiated buy request for item: 3)\n")
        if len(res.json()['res']) > 0:
            f.write("RESPONSE: Bought book %s\n" % res.json()['res'][0]['title'])
        else:
            f.write("RESPONSE: %s\n" % res.json()['msg'])


if __name__ == "__main__":
    frontendUri = sys.argv[1]
    callApiRequests(frontendUri)
