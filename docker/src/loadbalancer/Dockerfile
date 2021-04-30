FROM python:alpine
RUN apk add --no-cache python3
RUN apk add --update docker openrc
RUN rc-update add docker boot
WORKDIR ./loadbalancer
ADD . /loadbalancer
RUN pip install -r requirements.txt
CMD ["python","-u","loadBalancer.py"]