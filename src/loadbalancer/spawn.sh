pem_file=$1
loadbalancerdns=$2
frontenddns=$3
catalogdns_1=$4
catalogdns_2=$5
orderdns_1=$6
orderdns_2=$7

port=$8

if [ $port = 8084 ]; then
    ssh -o StrictHostKeyChecking=no -i $pem_file ec2-user@$orderdns_1 "cd order-server; python3 order.py http://$loadbalancerdns:8080  $orderdns_1 8084"
elif [ $port = 8085 ]; then
    ssh -o StrictHostKeyChecking=no -i $pem_file ec2-user@$orderdns_2 "cd order-server; python3 order.py http://$loadbalancerdns:8080  $orderdns_2  8085"
elif [ $port = 8082 ]; then
    ssh -o StrictHostKeyChecking=no -i $pem_file ec2-user@$catalogdns_1 "cd catalog-server; python3 catalog.py http://$frontenddns:8081 http://$loadbalancerdns:8080 $catalogdns_1 8082 '$catalogdns_1:8082|$catalogdns_2:8083'" 
elif [ $port = 8083 ]; then
    ssh -o StrictHostKeyChecking=no -i $pem_file ec2-user@$catalogdns_2 "cd catalog-server; python3 catalog.py http://$frontenddns:8081 http://$loadbalancerdns:8080 $catalogdns_2 8083 '$catalogdns_1:8082|$catalogdns_2:8083'"
else
    echo "wrong port"
fi