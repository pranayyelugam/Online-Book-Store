FROM python:alpine
ENV PORT 8082
ENV catalog http://0.0.0.0:8080
ENV balancer http://0.0.0.0:8085
WORKDIR ./order-server
ADD . /order-server
RUN pip install -r requirements.txt
CMD python order.py $catalog $balancer