FROM ubuntu:12.04

RUN apt-get update
RUN apt-get install -y python-pip

ADD . /src
WORKDIR /src

RUN make
