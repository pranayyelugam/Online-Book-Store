pip3 install -r requirements.txt
python ./frontend-server/frontend.py http://0.0.0.0:8080 http://0.0.0.0:8082 &
python ./catalog-server/catalog.py &
python ./order-server/order.py http://0.0.0.0:8080 &

sleep 2 &

python ./tests/tests.py  http://0.0.0.0:8081 http://0.0.0.0:8080 &

sleep 2 &

python ./client-process/client.py http://0.0.0.0:8081