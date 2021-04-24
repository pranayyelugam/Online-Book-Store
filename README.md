# Book-store

A multi-tier buyer-seller project

 **LOCAL EXECUTION **:
 To run the project locally:
  Execute **sh run.sh**.

 **AWS EXECUTION **:
 To run the project on AWS:
  1) Update the config.txt with the following
       - Add the key-pair file path in the first line
       - Add loadbalancer, frontend, catalog-1, catalog-2, order-1 and order-2 dns in new lines.
  2) After the above step is done execute the following **sh aws_run.sh $(cat config.txt)**
  3) The above commands will copy the code to the respective servers, installs python, installs the requirements and runs the flask app on the server.
  5) You can access the frontend server at http://frontenddns:8081/
  6) An example url to test would be http://frontenddns:8081/lookup/3

 **DOCKER EXECUTION **: 
To run the project on DOCKER:
  1) cd docker 
  2) Execute the following bash script **sh run_docker_images.sh** . This will pull the containers from docker hub and executes docker run for every micro      service locally.
  3) You can access the frontend server at http://0.0.0.0:8081/
  4) An example url to test would be http://0.0.0.0:8081/lookup/3
  
To kill the micro services in the docker containers:
  1) docker rm --force loadbalancer frontend catalog-1 catalog-2 order-1 order-2
  

All the above executions will also execute the client on your local system which calls the front-end server and outputs the response in to a text file in client-process folder called **ClientOutput.txt**

The above commands will also execute the tests on your local system which calls the front-end server, execute the tests and outputs the response in to a text file in tests folder called **tests.txt**


The project is developed using Flask and you are assumed to have Flask installed.

The project is currently run on localhost with debug mode enabled.
Ports 8080,8081,8082,8083,8084,8085 needs to be free for the project execution.

Please note:

1) Flask is needed for execution of the project.
2) run.sh & aws_run.sh will run all the processes and execute the test cases as well.
3) The loadbalancer, frontend, catalog-1, catalog-2, order-1 and order-2 servers will run on three ports 8080,8081,8082,8083,8084,8085 respectively.
4) client-process/client.py is the client which executes the front-end actions.
5) The output of the requests from the client.py is stored in ClientOutput.txt.
6) tests/tests.py contains test cases that cover the tests for search, lookup and buy requests respectively. 
7) The output of the testcases are logged in the file tests.txt.
8) tests.txt contain the result of the testcases as well as the response for the requests.
