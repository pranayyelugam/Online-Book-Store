pem_file=$1
loadbalancerdns=$2
frontenddns=$3
catalogdns_1=$4
catalogdns_2=$5
orderdns_1=$6
orderdns_2=$7

port=$8

if [ $port = 8084 ]; then
    ssh -i $pem_file ec2-user@$orderdns_1 "sudo yum install -y python3.7; cd order-server; python3 --version; sudo pip3 install -r requirements.txt; /usr/sbin/lsof -i:8084 -t | xargs kill -KILL ; python3 order.py http://$loadbalancerdns:8080  $orderdns_1 8084"
elif [ $port = 8085 ]; then
    ssh -i $pem_file ec2-user@$orderdns_2 "sudo yum install -y python3.7; cd order-server; python3 --version; sudo pip3 install -r requirements.txt; /usr/sbin/lsof -i:8085 -t | xargs kill -KILL ; python3 order.py http://$loadbalancerdns:8080  $orderdns_2 8085"
elif [ $port = 8082 ]; then
    ssh -i $pem_file ec2-user@$catalogdns_1 "sudo yum install -y python3.7; cd catalog-server; python3 --version; sudo pip3 install -r requirements.txt; /usr/sbin/lsof -i:8082 -t | xargs kill -KILL ;  python3 catalog.py http://$frontenddns:8081 http://$loadbalancerdns:8080 $catalogdns_1 8082 '$catalogdns_1:8082|$catalogdns_2:8083'" 
else
    ssh -i $pem_file ec2-user@$catalogdns_2 "sudo yum install -y python3.7; cd catalog-server; python3 --version; sudo pip3 install -r requirements.txt; /usr/sbin/lsof -i:8083 -t | xargs kill -KILL ;  python3 catalog.py http://$frontenddns:8081 http://$loadbalancerdns:8080 $catalogdns_2 8083 '$catalogdns_1:8082|$catalogdns_2:8083'"

