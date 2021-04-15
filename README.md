# Book-store

A multi-tier buyer-seller project

To run the project locally, execute **sh run.sh**.

To run the project on AWS:
  1) Update the config.txt with the following
       - Add the key-pair file path in the first line
       - Add catalog, order and frontend dns in the first, second and third line respectively.
  2) After the above step is done execute the following **sh aws_run.sh $(cat config.txt)**
 
The above commands will copy the code to the respective servers, installs python, installs the requirements and runs the flask app on the server.

The above commands will also execute the client on your local system which calls the front-end server and outputs the response in to a text file in client-process folder called **ClientOutput.txt**

The above commands will also execute the tests on your local system which calls the front-end server, execute the tests and outputs the response in to a text file in tests folder called **tests.txt**


The project is developed using Flask and you are assumed to have Flask installed.

The project is currently run on localhost with debug mode enabled.
Ports 8080,8081,8082 needs to be free for the project execution.

Please note:

1) Flask is needed for execution of the project.
2) run.sh & aws_run.sh will run all the 4 processes and execute the test cases as well.
3) The front-end, catalog and order servers will run on three ports 8081,8080,8082 respectively.
4) client.py is the client which executes the front-end actions.
5) The output of the requests from the client.py is stored in ClientOutput.txt.
6) tests.py contains test cases that cover the tests for search, lookup and buy requests respectively. Extensive test cases are present in the test document in the docs folder.
7) The output of the testcases are logged in the file tests.txt.
8) tests.txt contain the result of the testcases as well as the response for the requests.
