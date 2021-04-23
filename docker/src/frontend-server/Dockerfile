FROM python:alpine
ENV PORT 8081
ENV balancer http://loadbalancer:8080
WORKDIR ./frontend-server
ADD . /frontend-server
RUN pip install -r requirements.txt
CMD python frontend.py $balancer