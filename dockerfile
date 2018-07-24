FROM python:3.6.6-alpine3.6

COPY . /WebSocketGateway

WORKDIR /WebSocketGateway

RUN pip install -r requirement.txt

CMD ["python", "-OO", "main.py"]
