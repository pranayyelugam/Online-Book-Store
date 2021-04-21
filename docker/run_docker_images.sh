docker network create myNetwork &&
sleep 1
docker run --network=myNetwork -p 8085:8085 --name loadbalancer lb &
docker run --network=myNetwork -p 8081:8081 --name frontend fs &
docker run --network=myNetwork -p 8080:8080 --name catalog-1 cs &
docker run --network=myNetwork -p 8086:8080 --name catalog-2 cs &
docker run --network=myNetwork -p 8082:8082 --name order-1 os &
docker run --network=myNetwork -p 8087:8082 --name order-2 os