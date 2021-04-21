cd src &&
cd catalog-server &&
docker build -f Dockerfile --tag cs . &&
cd ../frontend-server &&
docker build -f Dockerfile --tag fs . &&
cd ../order-server &&
docker build -f Dockerfile --tag os . &&
cd ../loadbalancer &&
docker build -f Dockerfile --tag lb . &&
cd ../../