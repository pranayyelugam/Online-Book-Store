docker pull pranayyelugam/frontend &&
docker pull pranayyelugam/catalog &&
docker pull pranayyelugam/order &&
docker pull pranayyelugam/loadbalancer &&

docker network create pygmy &&
sleep 1
docker run --network=pygmy -p 8080:8080 --name loadbalancer pranayyelugam/loadbalancer &
sleep 7
docker run --network=pygmy -p 8081:8081 --name frontend pranayyelugam/frontend &
sleep 2
docker run --network=pygmy -p 8082:8082 --name catalog-1 --env PORT=8082 --env HOST=catalog-1 pranayyelugam/catalog  &
sleep 2
docker run --network=pygmy -p 8083:8083 --name catalog-2 --env PORT=8083 --env HOST=catalog-2  pranayyelugam/catalog &
sleep 2
docker run --network=pygmy -p 8084:8084 --name order-1 --env PORT=8084 --env HOST=order-1 pranayyelugam/order &
sleep 2
docker run --network=pygmy -p 8085:8085 --name order-2 --env PORT=8085 --env HOST=order-2 pranayyelugam/order &
sleep 5
python ../client-process/client.py http://0.0.0.0:8081 &
sleep 5
python ../tests/tests.py http://0.0.0.0:8081 http://0.0.0.0:8082 &