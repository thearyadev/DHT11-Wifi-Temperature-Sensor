FROM python:3.10.2-slim-buster

WORKDIR /temp-sensor
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

copy . .
RUN apt-get update
RUN apt-get update
RUN apt-get install nano
RUN apt-get install -y iputils-ping
RUN apt-get install -y net-tools
ENV TZ=America/Toronto

CMD cd web_server && python3 main.py
