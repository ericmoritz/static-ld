FROM ubuntu:12.04

RUN apt-get update
RUN apt-get install -y python-software-properties
RUN apt-add-repository ppa:chris-lea/node.js
RUN apt-get update
RUN apt-get install -y git build-essential nodejs python-pip python-dev python-virtualenv cucumber

# Test requirements
RUN mkdir /src
WORKDIR /src

RUN pip install pytest

ADD . /src
RUN make
RUN python setup.py install
RUN make acceptance
