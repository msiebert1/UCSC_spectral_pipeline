FROM ubuntu:latest
RUN apt-get update -y
RUN apt install libx11-dev -y
RUN apt-get install python3-pip -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pyraf
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
ENV iraf=/usr/lib/iraf