#!/bin/sh
set -ex

# check for env variables
if [ -z "$ES_INDEX" ]; then
    echo "Error: ES_INDEX not set"
    exit 2;
fi

if [ -z "$PRODUCT_HOSTNAME" ]; then
    echo "Error: PRODUCT_HOSTNAME not set"
    exit 2;
fi

# extract product from hostname
PRODUCT=$(echo $PRODUCT_HOSTNAME | cut -d. -f1)
ES_HOST="${ES_HOST:=elk.int.laws.africa:9200}"

# export from ES into ./es-export.jsonlines
rm -rf ./es-export.jsonlines
/usr/share/logstash/bin/logstash -f es_search_index_export.conf

# convert jsonlines into json
cat ./es-export.jsonlines | jq -sc > ./data/${PRODUCT}_search_index.json
