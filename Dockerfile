FROM python:3.8-slim-buster

ARG AWS_KEY
ARG AWS_SECRET
ARG AWS_REGION
ARG PRODUCT
ARG PRODUCT_DOMAIN

ENV PRODUCT ${PRODUCT}
ENV PRODUCT_DOMAIN ${PRODUCT_DOMAIN}

# install wget
RUN apt-get update && apt-get install -y wget tree

RUN mkdir /extraction/

COPY warc_processor.py /extraction/warc_processor.py
COPY requirements.txt /extraction/requirements.txt
COPY runner.sh /extraction/runner.sh

WORKDIR /extraction

# install requirements
RUN pip install -r requirements.txt

# configure aws cli
RUN aws configure set aws_access_key_id ${AWS_KEY}
RUN aws configure set aws_secret_access_key ${AWS_SECRET}
RUN aws configure set region ${AWS_REGION}

RUN chmod +x runner.sh
ENTRYPOINT [ "./runner.sh" ]
