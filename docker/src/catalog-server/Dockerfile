FROM python:alpine
ENV FRONTEND http://frontend:8081
ENV LOADBALANCER http://loadbalancer:8080
ENV REPLICALIST 'catalog-1:8082|catalog-2:8083'
ENV HOST 0.0.0.0
ENV PORT 8082
WORKDIR ./catalog-server
ADD . /catalog-server
RUN pip install -r requirements.txt
CMD python catalog.py $FRONTEND $LOADBALANCER $HOST $PORT $REPLICALIST 