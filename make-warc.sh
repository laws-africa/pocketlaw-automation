#!/bin/sh
set -ex

# check for env variables
if [ -z "$PRODUCT_HOSTNAME" ]; then
    echo "Error: PRODUCT_HOSTNAME not set"
    exit 2;
fi

# extract product from hostname
PRODUCT=$(echo $PRODUCT_HOSTNAME | cut -d. -f1)

ARCHIVE_FILE="./data/${PRODUCT}.warc.gz"
PRODUCT_URL="https://${PRODUCT_HOSTNAME}"

# Run wget

# the -Xs are to ignore gazettes
#   eg: /akn/za/officialGazette/government-gazette/2023-01-31/47974/eng@2023-01-31

wget --recursive --page-requisites --span-hosts --https-only --delete-after --no-directories \
    --domains ${PRODUCT_HOSTNAME},use.fontawesome.com,fonts.googleapis.com,code.highcharts.com,cdn.jsdelivr.net \
    --tries 3\
    -X '/akn/*/officialGazette/*' \
    -X '/akn/*/officialGazette/*/*' \
    -X '/akn/*/officialGazette/*/*/*' \
    -X '/akn/*/officialGazette/*/*/*/*' \
    -X '/akn/*/officialGazette/*/*/*/*/*' \
    --warc-file=data/$PRODUCT ${PRODUCT_URL}

# Run warc_processor.py with location to warc file
python3 ./warc_processor.py --hostname $PRODUCT_HOSTNAME --archive data/${ARCHIVE_FILE}
