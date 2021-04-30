pem_file=$1
loadbalancerdns=$2
frontenddns=$3
catalogdns_1=$4
catalogdns_2=$5
orderdns_1=$6
orderdns_2=$7


ssh -i $pem_file ec2-user@$orderdns_1 "/usr/sbin/lsof -i:8084 -t | xargs kill -KILL ;"

ssh -i $pem_file ec2-user@$orderdns_2 "/usr/sbin/lsof -i:8085 -t | xargs kill -KILL ;"

ssh -i $pem_file ec2-user@$loadbalancerdns "/usr/sbin/lsof -i:8080 -t | xargs kill -KILL ;"
ssh -i $pem_file ec2-user@$frontenddns "/usr/sbin/lsof -i:8081 -t | xargs kill -KILL ;"



ssh -i $pem_file ec2-user@$catalogdns_2 "/usr/sbin/lsof -i:8083 -t | xargs kill -KILL ;"

ssh -i $pem_file ec2-user@$catalogdns_1 "/usr/sbin/lsof -i:8082 -t | xargs kill -KILL ;"
