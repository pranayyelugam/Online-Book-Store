
printf "docker"  > ./src/loadbalancer/spawnConfig.txt

docker network create pygmy &&
sleep 1
docker run --network=pygmy -v "/var/run/docker.sock:/var/run/docker.sock" -p 8080:8080 --name loadbalancer pranay_lb &
sleep 2
docker run --network=pygmy -p 8081:8081 --name frontend pranay_fs &
sleep 2
docker run --network=pygmy -p 8082:8082 --name catalog-1 --env PORT=8082 --env HOST=catalog-1 pranay_cs  &
sleep 2
docker run --network=pygmy -p 8083:8083 --name catalog-2 --env PORT=8083 --env HOST=catalog-2 pranay_cs &
sleep 2
docker run --network=pygmy -p 8084:8084 --name order-1 --env PORT=8084 --env HOST=order-1 pranay_os &
sleep 2
docker run --network=pygmy -p 8085:8085 --name order-2 --env PORT=8085 --env HOST=order-2 pranay_os &
sleep 5
python ../client-process/client.py http://0.0.0.0:8081 &
sleep 5
python ../tests/tests.py http://0.0.0.0:8081 http://0.0.0.0:8082 &