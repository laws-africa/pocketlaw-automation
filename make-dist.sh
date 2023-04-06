#!/bin/sh
set -ex

# TODO: use a function
# check for env variables
if [ -z "$PRODUCT_HOSTNAME" ]; then
    echo "Error: PRODUCT_HOSTNAME not set"
    exit 2;
fi

# extract product from hostname
PRODUCT=$(echo $PRODUCT_HOSTNAME | cut -d. -f1)

# copy search index into place
mkdir -p data/files/$PRODUCT/base/
cp data/${PRODUCT}_search_index.json data/files/$PRODUCT/base/search_index.json

# Run warc_processor.py with location to warc file
python3 ./warc_processor.py --hostname $PRODUCT_HOSTNAME --archive data/${PRODUCT}.warc.gz
python3 ./warc_processor.py --hostname $PRODUCT_HOSTNAME --archive data/${PRODUCT}.warc.gz --dist

tree data
