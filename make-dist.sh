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

# extract product from hostname
PRODUCT=$(echo $PRODUCT_HOSTNAME | cut -d. -f1)
ARCHIVE_FILE="./data/${PRODUCT}.warc.gz"

# configure aws cli
aws configure set aws_access_key_id ${AWS_KEY}
aws configure set aws_secret_access_key ${AWS_SECRET}
aws configure set region ${AWS_REGION:-eu-west-1}

# copy search index into place
cp data/${PRODUCT}_search_index.json data/files/$PRODUCT/base/search_index.json

# Run warc_processor.py with location to warc file
python3 ./warc_processor.py --hostname $PRODUCT_HOSTNAME --archive data/${ARCHIVE_FILE} --dist

tree data

# copy in the content pack files
for f in data/dist/$PRODUCT_*.tgz; do
  aws s3 cp $f s3://pocketlaw/$PRODUCT/content_packs/
done

# copy in the pack list last, this is what pocketlaw checks for updates
aws s3 cp data/dist/$PRODUCT_packs.json s3://pocketlaw/$PRODUCT/
