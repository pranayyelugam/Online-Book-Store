FROM python:alpine
ENV FRONTEND http://0.0.0.0:8081
ENV LOADBALANCER http://0.0.0.0:8080
ENV REPLICALIST '0.0.0.0:8082|0.0.0.0:8083'
ENV HOST 0.0.0.0
ENV PORT 8082
WORKDIR ./catalog-server
ADD . /catalog-server
RUN pip install -r requirements.txt
CMD python catalog.py $FRONTEND $LOADBALANCER $HOST $PORT $REPLICALIST 