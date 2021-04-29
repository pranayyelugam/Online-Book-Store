FROM python:alpine
WORKDIR ./loadbalancer
ADD . /loadbalancer
RUN pip install -r requirements.txt
CMD ["python","-u","loadBalancer.py"]