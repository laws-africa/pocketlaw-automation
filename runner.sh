#!/bin/sh
set -ex

# TODO: use a function
# check for env variables
if [ -z "$PRODUCT" ]; then
    echo "Error: PRODUCT not set"
    exit 2;
fi

if [ -z "$PRODUCT_DOMAIN" ]; then
    echo "Error: PRODUCT_DOMAIN not set"
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

ARCHIVE_FILE="./${PRODUCT}.warc.gz"
PRODUCT_URL="https://${PRODUCT_DOMAIN}"
MEDIA_BASE_URL="media.${PRODUCT_DOMAIN}"

# configure aws cli
aws configure set aws_access_key_id ${AWS_KEY}
aws configure set aws_secret_access_key ${AWS_SECRET}
aws configure set region ${AWS_REGION}

# Run wget
wget --recursive --page-requisites \
    --domains ${PRODUCT_DOMAIN},${MEDIA_BASE_URL},use.fontawesome.com,fonts.googleapis.com,code.highcharts.com,cdn.jsdelivr.net \
    --span-hosts \
    --https-only --reject pdf,rtf,doc,docx,DOC \
    --delete-after \
    --warc-file=$PRODUCT \
    --no-directories \
    ${PRODUCT_URL}

# Run warc_processor.py with location to warc file
python /extraction/warc_processor.py --product $PRODUCT --archive ${ARCHIVE_FILE}

tree .
