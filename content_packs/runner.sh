#!/bin/sh
set -ex

# TODO: use a function
# check for env variables
if [ -z "$PRODUCT_HOSTNAME" ]; then
    echo "Error: PRODUCT_HOSTNAME not set"
    exit 2;
fi

if [ -z "$AWS_KEY" ]; then
    echo "Error: AWS_KEY not set"
    exit 2;
fi

if [ -z "$AWS_SECRET" ]; then
    echo "Error: AWS_SECRET not set"
    exit 2;
fi

if [ -z "$AWS_REGION" ]; then
    echo "Error: AWS_REGION not set"
    exit 2;
fi

# extract product from hostname
PRODUCT=$(echo $PRODUCT_HOSTNAME | cut -d. -f1)

ARCHIVE_FILE="./${PRODUCT}.warc.gz"
PRODUCT_URL="https://${PRODUCT_HOSTNAME}"

# configure aws cli
aws configure set aws_access_key_id ${AWS_KEY}
aws configure set aws_secret_access_key ${AWS_SECRET}
aws configure set region ${AWS_REGION}

# Run wget
wget --recursive --page-requisites --span-hosts --https-only --delete-after --no-directories \
    --domains ${PRODUCT_HOSTNAME},use.fontawesome.com,fonts.googleapis.com,code.highcharts.com,cdn.jsdelivr.net \
    --warc-file=$PRODUCT \
    ${PRODUCT_URL}

# Run warc_processor.py with location to warc file
python /extraction/warc_processor.py --hostname $PRODUCT_HOSTNAME --archive ${ARCHIVE_FILE}

tree .
