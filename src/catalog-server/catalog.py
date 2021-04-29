from flask import Flask, jsonify, g
import json, sys, os, time
from json import JSONEncoder
import sqlite3
import requests
from flask import g
import threading
import random

app = Flask(__name__)

# Write lock needed for primary based consistency
lock = threading.Lock()


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


scriptDir = os.path.dirname(__file__)
rel_database_path = "database.txt"
rel_requests_path = "requests.txt"
databasePath = os.path.join(scriptDir, rel_database_path)
requestsPath = os.path.join(scriptDir, rel_requests_path)

"""
CatalogItem class object
"""


class CatalogItem:
    def __init__(self, itemNumber, title, stock, cost, topic):
        self.itemNumber = itemNumber
        self.title = title
        self.stock = stock
        self.cost = cost
        self.topic = topic


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


def query_db(query, args=(), one=False):
    try:
        cur = get_db().execute(query, args)
        get_db().commit()
    except Exception as E:
        print("error", E)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def getAllCatalogItems():
    """Gets the catalog items from the database

    Args:

    Returns:
    list: a list of all catalog items
    """
    with app.app_context():
        books = query_db("select * from books")
    return books


def findItemByTopic(topic):
    """Gets the catalog items from the database

    Args:
        topic(str): the topic type

    Returns:
    list: a list of catalog items matching the topic
    """
    with app.app_context():
        books = query_db("select * from books where topic = ?", [topic])
    return books


def findItemByNumber(itemNumber):
    """Gets the catalog items from the database

    Args:
        itemNumber(str): the item number

    Returns:
    item: the catalog item matching the item number
    """
    with app.app_context():
        books = query_db("select * from books where itemNumber = ?", [itemNumber])
    return books


def updateStock(itemNumber, value):
    """Update the value of the stock with the given value for the item

    Args:
        itemNumber(str): the item number
        value(str): the value of the stock

    Returns:
    item: the catalog item matching the item number
    """
    with app.app_context():
        books = query_db(
            "update books set stock = ? where itemNumber = ?", [value, itemNumber]
        )
        books = query_db("select * from books where itemNumber = ?", [itemNumber])
    return books


def reduceStock(itemNumber):
    """Reduces the value of the stock by 1

    Args:
        itemNumber(str): the item number

    Returns:
    item: the catalog item matching the item number
    """
    with app.app_context():
        books = query_db(
            "update books set stock = cast((cast(stock as int) - 1) as text) where itemNumber = ?",
            [itemNumber],
        )
        books = query_db("select * from books where itemNumber = ?", [itemNumber])
    return books


def updateCost(itemNumber, value):
    """Update the value of the cost with the given value for the item

    Args:
        itemNumber(str): the item number
        value(str): the value of the cost

    Returns:
    item: the catalog item matching the item number
    """
    with app.app_context():
        books = query_db(
            "update books set cost = ? where itemNumber = ?", [value, itemNumber]
        )
        books = query_db("select * from books where itemNumber = ?", [itemNumber])
    return books


class CatalogItemEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, CatalogItem):
            return object.__dict__
        else:
            return json.JSONEncoder.default(self, object)


def getUrl(host, port):
    """ Constructs a Url from the input host and port"""
    return "http://" + host + ":" + port


# ROUTE: /query/itemNumber
@app.route("/query/<int:itemNumber>")
def queryByItemNmber(itemNumber):
    resultItems = findItemByNumber(itemNumber)
    if len(resultItems):
        return CatalogItemEncoder().encode(resultItems)
    else:
        return {}


# ROUTE: /query/topic
@app.route("/query/<string:topic>")
def queryByItemTopic(topic):
    resultItems = findItemByTopic(topic)
    if len(resultItems):
        return CatalogItemEncoder().encode(resultItems)
    else:
        return {}


# ROUTE: /updateStock/itemNumber/value
@app.route("/updateStock/<int:itemNumber>/<int:value>")
def updateStockRoute(itemNumber, value, dataLoading=False):
    """ Update the stock value of an item with a given value """

    requests.get(app.config.get("frontend_uri") + "/invalidate/" + str(itemNumber))
    with lock:
        response = updateStock(itemNumber, value)
        ## TODO ##
        # How do I get the endpoint of other servers here?
        catalogList = app.config.get("replicaList")
        endpoints = catalogList.split("|")
        endpointUrlsExcludingCurrentServer = []
        for x in endpoints:
            host, port = x.split(":")
            if port == app.config.get("port") and host == app.config.get("host"):
                continue
            else:
                endpointUrlsExcludingCurrentServer.append(getUrl(host, port))

        for endpoint in endpointUrlsExcludingCurrentServer:
            try:
                replicaUpdateRequest = requests.get(
                    endpoint
                    + "/update_replica_stock/"
                    + str(itemNumber)
                    + "/"
                    + str(value)
                )
            except Exception as E:
                print("Exception occurred while writing to replica")

    storeInDatabase("updateStock/" + str(itemNumber) + "/" + str(value), requestsPath)
    return CatalogItemEncoder().encode(response)


# ROUTE: /reduceStock/itemNumber
@app.route("/reduceStock/<int:itemNumber>")
def reduceOneStock(itemNumber, dataLoading=False):
    """ Reduces the stock value by 1 """

    requests.get(app.config.get("frontend_uri") + "/invalidate/" + str(itemNumber))
    with lock:
        response = reduceStock(itemNumber)
        catalogList = app.config.get("replicaList")
        endpoints = catalogList.split("|")
        endpointUrlsExcludingCurrentServer = []
        for x in endpoints:
            host, port = x.split(":")
            if port == app.config.get("port") and host == app.config.get("host"):
                continue
            else:
                endpointUrlsExcludingCurrentServer.append(getUrl(host, port))

        for endpoint in endpointUrlsExcludingCurrentServer:
            try:
                replicaUpdateRequest = requests.get(
                    endpoint + "/update_replica/" + str(itemNumber)
                )
            except Exception as E:
                print("Exception occurred while writing to replica")

    storeInDatabase("reduceStock/" + str(itemNumber), requestsPath)
    return CatalogItemEncoder().encode(response)


# ROUTE: /updateCost/itemNumber/value
@app.route("/updateCost/<int:itemNumber>/<int:value>")
def updateCostRoute(itemNumber, value, dataLoading=False):
    """ Update the cost value of an item with a given value """

    requests.get(app.config.get("frontend_uri") + "/invalidate/" + str(itemNumber))
    with lock:
        response = updateCost(itemNumber, value)
        catalogList = app.config.get("replicaList")
        endpoints = catalogList.split("|")
        endpointUrlsExcludingCurrentServer = []
        for x in endpoints:
            host, port = x.split(":")
            if port == app.config.get("port") and host == app.config.get("host"):
                continue
            else:
                endpointUrlsExcludingCurrentServer.append(getUrl(host, port))

        for endpoint in endpointUrlsExcludingCurrentServer:
            try:
                replicaUpdateRequest = requests.get(
                    endpoint
                    + "/update_replica_cost/"
                    + str(itemNumber)
                    + "/"
                    + str(value)
                )
            except Exception as E:
                print("Exception occurred while writing to replica")
    storeInDatabase("updateCost/" + str(itemNumber) + "/" + str(value), requestsPath)
    return CatalogItemEncoder().encode(response)


@app.route("/update_replica/<string:itemNumber>", methods=["GET"])
def updateReplica(itemNumber):
    """ Update the replica when a buy request is received """
    try:
        with lock:
            response = reduceStock(itemNumber)
    except Exception:
        return {"res": "Exception in updating the replica"}
    else:
        return {"res": "Something went wrong while updating `the replica"}


@app.route("/update_replica_stock/<string:itemNumber>/<string:quantity>", methods=["GET"])
def updateReplicaStock(itemNumber, quantity):
    """ Update the stock value of an item with a given value in the replica """

    try:
        with lock:
            response = updateStock(itemNumber, quantity)
    except Exception:
        return {"res": "Exception in updating the replica"}
    else:
        return {"res": "Something went wrong while updating the replica"}


@app.route(
    "/update_replica_cost/<string:itemNumber>/<string:quantity>", methods=["GET"]
)
def updateReplicaCost(itemNumber, quantity):
    """ Update the cost value of an item with a given value in the replica """

    try:
        with lock:
            response = updateCost(itemNumber, quantity)
    except Exception:
        return {"res": "Exception in updating the replica"}
    else:
        return {"res": "Something went wrong while updating the replica"}


@app.route("/")
def checkAlive():
    return "Hey! I'm well and alive. Don't worry about me"

@app.route("/resync/<string:target>", methods=['GET'])
def syncWithAliveTargetDb(target):
    target = "http://" + target
    print(target + "=========")
    resp = requests.get(target+"/get_db")
    stocks = resp.json()['stocks']
    db = None
    for itemNumber in stocks:
        db = updateStock(itemNumber, stocks[itemNumber])
        db = updateCost(itemNumber, stocks[itemNumber])
    print(db)
    return resp.json()

@app.route("/get_db", methods=['GET'])
def getCurrentDbState():
    stock_data = {}
    cost_data = {}
    with lock:
        books = getAllCatalogItems()
        for book in books:
            stock_data[book['itemNumber']] = book['stock']
            cost_data[book['itemNumber']] = book['cost']
    return ({
        'stocks': stock_data,
        'costs': cost_data
    })



def storeInDatabase(res, fileName):
    """Store the update requests in a log file

    Args:
        res(str): request type
        fileName(str): the name of the log file

    Returns:

    """
    with open(fileName, "a") as filehandle:
        filehandle.write(str(res))
        filehandle.write("\n")


if __name__ == "__main__":
    """
    Create the books table from the data json if the table is not already created.
    Insert the data in to the table only when the table is created for the first time.
    And start the Flask service.
    """
    app.config["frontend_uri"] = sys.argv[1]
    app.config["loadbalancer_uri"] = sys.argv[2]
    app.config["host"] = sys.argv[3]
    app.config["port"] = sys.argv[4]
    app.config["replicaList"] = sys.argv[5]

    scriptDir = os.path.dirname(__file__)
    outputPath = "./database_{}.db".format(app.config.get("port"))
    DATABASE = os.path.join(scriptDir, outputPath)
    rel_requests_path = "requests_{}.txt".format(app.config.get("port"))
    requestsPath = os.path.join(scriptDir, rel_requests_path)
    data_path = os.path.join(scriptDir, './data.json')
    f = open(data_path)
    json_data = json.load(f)

    try:
        with app.app_context():
            cur = get_db().cursor()
            CREATE_SQL =  "CREATE TABLE IF NOT EXISTS BOOKS (itemNumber text, title text,  stock text, cost text, topic text);"
            DELETE_SQL = "DROP TABLE IF EXISTS BOOKS;"    

            #create cache table
            cur.execute(DELETE_SQL)
            cur.execute(CREATE_SQL)

            books = []
            for row in json_data['books']:
                itemNumber = row["itemNumber"]
                title = row["title"]
                stock = row["stock"]
                cost = row["cost"]
                topic = row["topic"]
                data = (itemNumber, title, stock, cost, topic)
                books.append(data)
            try:
                cur = get_db().cursor()
                cur.executemany("insert into BOOKS values(?,?,?,?,?)", books)
            except Exception as E:
                print("Errorrr", E)
            else:
                get_db().commit()
                print("data inserted")
    except Exception as E:
        print("Error :,")
        print(E)

    host = app.config["host"]
    port = app.config["port"]

    # register to the loadbalancer as soon as server is active
    res = requests.get(
        app.config.get("loadbalancer_uri") + "/@register_catalog@" + host + ":" + port
    )

    app.run(host='0.0.0.0', port=port, threaded=True)
