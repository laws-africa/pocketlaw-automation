#!/bin/sh
set -ex

./make-search-index.sh
./make-warc.sh
./make-dist.sh
./dist.sh
