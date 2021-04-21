FROM python:alpine
ENV PORT 8080
ENV FRONTEND http://0.0.0.0:8081
WORKDIR ./catalog-server
ADD . /catalog-server
RUN pip install -r requirements.txt
CMD python catalog.py $FRONTEND