

pem_file=$1
catalogdns=$2
orderdns=$3
frontenddns=$4

pip3 install -r requirements.txt

scp -i $pem_file -r ./catalog-server ec2-user@$catalogdns:/home/ec2-user
scp -i $pem_file -r ./order-server ec2-user@$orderdns:/home/ec2-user
scp -i $pem_file -r ./frontend-server ec2-user@$frontenddns:/home/ec2-user


ssh -i $pem_file ec2-user@$catalogdns "sudo yum install -y python3.7; cd catalog-server; python3 --version; sudo pip3 install -r requirements.txt;  python3 catalog.py" & 

ssh -i $pem_file ec2-user@$orderdns "sudo yum install -y python3.7; cd order-server; python3 --version; sudo pip3 install -r requirements.txt; python3 order.py http://$catalogdns:8080" &

ssh -i $pem_file ec2-user@$frontenddns "sudo yum install -y python3.7; cd frontend-server; python3 --version; sudo pip3 install -r requirements.txt;  python3 frontend.py http://$catalogdns:8080 http://$orderdns:8082" &

sleep 2

python ./tests/tests.py "http://$frontenddns:8081" "http://$catalogdns:8080"

sleep 2

python ./client-process/client.py "http://$frontenddns:8081" 