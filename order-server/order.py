from flask import Flask
import json, sys, requests
app = Flask(__name__)


# ROUTE: /buy/itemNumber
@app.route('/buy/<int:itemNumber>')
def buyRequestForItem(itemNumber):
    queryResponse = requests.get(app.config.get('catalog_uri') + '/query/' + str(itemNumber)).json()
    if queryResponse:
        stock = int(queryResponse[0]["stock"]) - 1
        if (stock >= 0):
            try:
                updateResponse =  requests.get(app.config.get('catalog_uri') + '/reduceStock/'+ str(itemNumber))
                updateResponse.raise_for_status()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}') 
            except Exception as err:
                print(f'Other error occurred: {err}')  
            else:
                return updateResponse.text
        else:
            print("Stock for item number %d is less than 0" % itemNumber )
            return {}
    else:
        return {}
        

if __name__ == "__main__":
    app.config['catalog_uri'] = sys.argv[1]
    app.run(host='0.0.0.0', port=8082, debug=True)