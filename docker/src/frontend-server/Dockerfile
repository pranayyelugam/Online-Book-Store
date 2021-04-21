FROM python:alpine
ENV PORT 8081
ENV catalog http://0.0.0.0:8080
ENV order http://0.0.0.0:8082
ENV balancer http://0.0.0.0:8085
WORKDIR ./frontend-server
ADD . /frontend-server
RUN pip install -r requirements.txt
CMD python frontend.py $catalog $order $balancer