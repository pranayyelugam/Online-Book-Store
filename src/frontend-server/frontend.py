from flask import Flask
import requests, json, sys
from cache import Cache

app = Flask(__name__)
cache = Cache()


# ROUTE: /search/topic
@app.route("/search/<string:topic>")
def search(topic):
    cacheItem = cache.get(str(topic))
    if cacheItem != "not found":
        return cacheItem
    res = requests.get(app.config.get("loadbalancer_uri") + "/@query@" + str(topic))
    res = prettifyOutput(res, "Item not present for topic %s" % topic)
    cache.put(str(topic), res)
    return res


# ROUTE: /lookup/itemNumber
@app.route("/lookup/<int:itemNumber>")
def lookup(itemNumber):
    cacheItem = cache.get(str(itemNumber))
    if cacheItem != "not found":
        return cacheItem
    res = requests.get(
        app.config.get("loadbalancer_uri") + "/@query@" + str(itemNumber)
    )
    res = prettifyOutput(res, "Item not present for item number %d" % itemNumber)
    cache.put(str(itemNumber), res)
    return res


# ROUTE: /buy/itemNumber
@app.route("/buy/<string:itemNumber>")
def buy(itemNumber):
    res = requests.get(app.config.get("loadbalancer_uri") + "/@buy@" + itemNumber)
    res = prettifyOutput(res, "The item is out of stock")
    return res


@app.route("/invalidate/<string:key>")
def eraseKeyFromCache(key):
    cache.erase(str(key))
    return "True"


@app.route("/")
def root():
    return "True"


def prettifyOutput(response, errorMsg):
    jsonResponse = response.json()
    res = None
    if len(jsonResponse) > 0:
        result = {"res": jsonResponse, "msg": ""}
    else:
        result = {"res": "", "msg": errorMsg}
    res = result
    return res


if __name__ == "__main__":
    app.config["loadbalancer_uri"] = sys.argv[1]
    app.run(host="0.0.0.0", port=8081)
