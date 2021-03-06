
printf "local"  > ./src/loadbalancer/spawnConfig.txt

python ./src/loadbalancer/loadBalancer.py &
sleep 2 
python ./src/frontend-server/frontend.py http://0.0.0.0:8080 &
sleep 2 
python ./src/catalog-server/catalog.py http://0.0.0.0:8081 http://0.0.0.0:8080 0.0.0.0 8082 '0.0.0.0:8082|0.0.0.0:8083' &
sleep 2 
python ./src/catalog-server/catalog.py http://0.0.0.0:8081 http://0.0.0.0:8080 0.0.0.0 8083 '0.0.0.0:8082|0.0.0.0:8083' &
sleep 2 
python ./src/order-server/order.py http://0.0.0.0:8080 0.0.0.0 8084 &
sleep 2 
python ./src/order-server/order.py http://0.0.0.0:8080 0.0.0.0 8085 &
sleep 2 
python ./tests/tests.py  http://0.0.0.0:8081 http://0.0.0.0:8082 &
sleep 2 
python ./client-process/client.py http://0.0.0.0:8081 &