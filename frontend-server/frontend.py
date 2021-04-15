from flask import Flask
import requests, json, sys
app = Flask(__name__)

# ROUTE: /search/topic
@app.route('/search/<string:topic>')
def search(topic):
    res = requests.get(app.config.get('catalog_uri') + '/query/' + str(topic))
    jsonResponse =  res.json()
    if len(jsonResponse)>0:
        result = {
            'res' : jsonResponse,
            'msg' : ''
        }
        return result
    else:
        result = {
            'res' : '',
            'msg' : 'Item not present for topic %s' % topic
        }
        return result

# ROUTE: /lookup/itemNumber
@app.route('/lookup/<int:itemNumber>')
def lookup(itemNumber):
    res = requests.get(app.config.get('catalog_uri') + '/query/' + str(itemNumber))
    jsonResponse =  res.json()
    if len(jsonResponse)>0:
        result = {
            'res' : jsonResponse,
            'msg' : ''
        }
        return result
    else:
        result = {
            'res' : '',
            'msg' : 'Item not present for item number %d' % itemNumber
        }
        return result

# ROUTE: /buy/itemNumber
@app.route('/buy/<int:itemNumber>')
def buy(itemNumber):
    res = requests.get(app.config.get('order_uri') + '/buy/' + str(itemNumber))
    jsonResponse =  res.json()
    if len(jsonResponse)>0:
        result = {
            'res' : jsonResponse,
            'msg' : ''
        }
        return result
    else:
        result = {
            'res' : '',
            'msg' : 'The item is out of stock'
        }
        return result

if __name__ == "__main__":
    app.config['catalog_uri'] = sys.argv[1]
    app.config['order_uri'] = sys.argv[2]
    app.run(host='0.0.0.0', port=8081, debug=True)