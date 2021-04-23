FROM python:alpine
ENV PORT 8084
ENV LOADBALANCER http://loadbalancer:8080
ENV HOST 0.0.0.0
WORKDIR ./order-server
ADD . /order-server
RUN pip install -r requirements.txt
CMD python order.py $LOADBALANCER $HOST $PORT 