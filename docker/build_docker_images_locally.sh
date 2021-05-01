cd src &&
cd loadbalancer &&
docker build -f Dockerfile --tag pranay_lb . &&
cd ../frontend-server &&
docker build -f Dockerfile --tag pranay_fs . &&
cd ../catalog-server &&
docker build -f Dockerfile --tag pranay_cs . &&
cd ../order-server &&
docker build -f Dockerfile --tag pranay_os . &&
cd ../../