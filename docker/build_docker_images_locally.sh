cd src &&
cd loadbalancer &&
docker build -f Dockerfile --tag lb . &&
cd ../frontend-server &&
docker build -f Dockerfile --tag fs . &&
cd ../catalog-server &&
docker build -f Dockerfile --tag cs . &&
cd ../order-server &&
docker build -f Dockerfile --tag os . &&
cd ../../