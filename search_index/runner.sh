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

if [ -z "$CSV_OUTPUT_DEST" ]; then
    echo "Error: CSV_OUTPUT_DEST not set"
    exit 2;
fi

if [ -z "$JSON_OUTPUT_DEST" ]; then
    echo "Error: JSON_OUTPUT_DEST not set"
    exit 2;
fi

# details from ES index into CSV
# TODO: command may be different based on OS
logstash -f es_search_index_export.conf

# convert CSV into JSON
python index_processor.py --csv-input $CSV_OUTPUT_DEST --json-output $JSON_OUTPUT_DEST
