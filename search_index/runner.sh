#!/bin/sh
set -ex

# details from ES index into CSV
logstash -f es_search_index_export.conf

# convert CSV into JSON
python index_processor.py
