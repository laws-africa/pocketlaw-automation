#!/bin/sh

ARCHIVE_FILE="./${PRODUCT}.warc.gz"
PRODUCT_URL="https://${PRODUCT_DOMAIN}"

# Run wget
wget --page-requisites \
    --domains ${PRODUCT_DOMAIN},media.zimlii.org,use.fontawesome.com,fonts.googleapis.com,code.highcharts.com \
    --span-hosts \
    --https-only --reject pdf,rtf,doc,docx,DOC \
    --delete-after \
    --warc-file=$PRODUCT \
    --no-directories ${PRODUCT_URL}

# Run warc_processor.py with location to warc file
python /extraction/warc_processor.py --product $PRODUCT --archive ${ARCHIVE_FILE}

tree .
