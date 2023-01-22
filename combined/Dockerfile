FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-pip apt-transport-https wget tree

# setup logstash
RUN wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
RUN echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" > /etc/apt/sources.list.d/elastic-7.x.list
RUN apt-get update && apt-get install -y logstash
RUN /usr/share/logstash/bin/logstash-plugin install logstash-input-elasticsearch
RUN /usr/share/logstash/bin/logstash-plugin install logstash-output-csv

ENV AWS_KEY=
ENV AWS_SECRET=
ENV AWS_REGION=
ENV PRODUCT_HOSTNAME=
ENV ES_HOST=
ENV ES_INDEX=

RUN mkdir /extraction/
RUN mkdir /extraction/data

# install python requirements
COPY requirements.txt /extraction/
RUN pip install -r /extraction/requirements.txt

COPY *.sh *.py *.conf /extraction/
WORKDIR /extraction
RUN chmod +x *.sh

ENTRYPOINT [ "./make-all.sh" ]
