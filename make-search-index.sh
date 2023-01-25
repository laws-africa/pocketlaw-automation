#!/bin/sh
set -ex

# check for env variables
if [ -z "$ES_HOST" ]; then
    echo "Error: ES_HOST not set"
    exit 2;
fi

if [ -z "$ES_INDEX" ]; then
    echo "Error: ES_INDEX not set"
    exit 2;
fi

if [ -z "$JSON_OUTPUT_DEST" ]; then
    echo "Error: JSON_OUTPUT_DEST not set"
    exit 2;
fi

# export from ES into ./es-export.jsonlines
rm -rf ./es-export.jsonlines
/usr/share/logstash/bin/logstash -f es_search_index_export.conf

# convert jsonlines into json
cat ./es-export.jsonlines | jq -sc > $JSON_OUTPUT_DEST
