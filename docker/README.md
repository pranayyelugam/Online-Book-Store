**DOCKER EXECUTION**:
To run the project on DOCKER:
1) cd docker
2) Execute the following bash script **sh run_docker_images.sh**
3) This will pull the containers from docker hub and executes docker run for every micro service locally.
4) You can access the frontend server at http://0.0.0.0:8081/
5) An example url to test would be http://0.0.0.0:8081/lookup/3


  
To kill the micro services in the docker containers:

**docker rm --force loadbalancer frontend catalog-1 catalog-2 order-1 order-2**
