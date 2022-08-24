FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pyraf
RUN pip3 install pyraf==2.2.1
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
