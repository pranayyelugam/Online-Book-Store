pip3 install -r requirements.txt
python ./catalog-server/catalog.py http://0.0.0.0:8081 &
python ./order-server/order.py http://0.0.0.0:8080 