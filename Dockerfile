FROM python:3.8-slim-buster

ENV AWS_KEY=
ENV AWS_SECRET=
ENV AWS_REGION=
ENV PRODUCT_HOSTNAME=

# install wget
RUN apt-get update && apt-get install -y wget tree

RUN mkdir /extraction/

COPY warc_processor.py /extraction/warc_processor.py
COPY requirements.txt /extraction/requirements.txt
COPY runner.sh /extraction/runner.sh

WORKDIR /extraction

# install requirements
RUN pip install -r requirements.txt

RUN chmod +x runner.sh
ENTRYPOINT [ "./runner.sh" ]
