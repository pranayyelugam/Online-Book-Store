from flask import Flask
import json, sys, requests, random

app = Flask(__name__)


@app.route("/")
def checkAlive():
    return "Hey! I'm well and alive. Don't worry about me"


# ROUTE: /buy/itemNumber
@app.route("/buy/<int:itemNumber>")
def buyRequestForItem(itemNumber):
    queryResponse = requests.get(
        app.config.get("loadbalancer_uri") + "/@query@" + str(itemNumber)
    ).json()
    if queryResponse:
        stock = int(queryResponse[0]["stock"]) - 1
        if stock >= 0:
            try:
                updateResponse = requests.get(
                    app.config.get("loadbalancer_uri")
                    + "/@reduceStock@"
                    + str(itemNumber)
                )
                updateResponse.raise_for_status()
            except HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
            except Exception as err:
                print(f"Other error occurred: {err}")
            else:
                return updateResponse.content
        else:
            print("Stock for item number %d is less than 0" % itemNumber)
            return {}
    else:
        return {}


if __name__ == "__main__":
    app.config["loadbalancer_uri"] = sys.argv[1]
    app.config["host"] = sys.argv[2]
    app.config["port"] = sys.argv[3]

    host = app.config["host"]
    port = app.config["port"]

    res = requests.get(
        app.config.get("loadbalancer_uri") + "/@register_order@" + host + ":" + port
    )

    app.run(host='0.0.0.0', port=port)
