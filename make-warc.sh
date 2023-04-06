#!/bin/sh
set -ex

# check for env variables
if [ -z "$PRODUCT_HOSTNAME" ]; then
    echo "Error: PRODUCT_HOSTNAME not set"
    exit 2;
fi

# extract product from hostname
PRODUCT=$(echo $PRODUCT_HOSTNAME | cut -d. -f1)
PRODUCT_URL="https://${PRODUCT_HOSTNAME}"

# Run wget

# the -Xs are to ignore gazettes
#   eg: /akn/za/officialGazette/government-gazette/2023-01-31/47974/eng@2023-01-31

wget --recursive --page-requisites --span-hosts --https-only --delete-after --no-directories \
    --domains ${PRODUCT_HOSTNAME},${PRODUCT}-files.s3.amazonaws.com,use.fontawesome.com,fonts.googleapis.com,www.googletagmanager.com \
    --tries 3 --read-timeout 300 \
    -X '/akn/*/officialGazette/*' \
    -X '/akn/*/officialGazette/*/*' \
    -X '/akn/*/officialGazette/*/*/*' \
    -X '/akn/*/officialGazette/*/*/*/*' \
    -X '/akn/*/officialGazette/*/*/*/*/*' \
    --warc-file=data/$PRODUCT ${PRODUCT_URL}
