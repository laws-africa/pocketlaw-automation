# pocketlaw-automation

Handy scripts to support PocketLaw. This repo includes:
* Script to automate the generation of content packs
* Script to automate the generation of the offline search index

## Docker

This repo builds a single Docker image for both content extraction and building the search index.

1. Build the image:
    ```
    docker build -t pl-content .
    ```

2. Build a volume to be attached to the crawl image:
    ```
    mkdir data
    ```

3. Run the container in detached mode with the required environment variables for the current product:
    ```
    docker run -d \
        -v $(pwd)/data:/extraction/data \
        -e PRODUCT_HOSTNAME="zimlii.org" \
        -e ES_INDEX="zimlii,zimlii_*" \
        -e AWS_REGION="eu-west-1" \
        -e AWS_KEY="<YOUR_AWS_CLI_KEY>" \
        -e AWS_SECRET="<YOUR_AWS_CLI_SECRET>" \
        pl-content
    ```

### Content Packs

To generate content packs from a `zimlii.warc` archive:

```bash
python warc_processor.py --product zimlii --archive ./zimlii.warc
```

All generated files are stored in the files folder as follows:

```
    .
    ├── Dockerfile
    ├── README.md
    ├── files
    │   └── zimlii
    │       ├── base
    │       │   ├── data.warc.gz
    │       │   ├── index.jsonlines
    │       │   └── manifest.json
    │       ├── caselaw
    │       │   ├── data.warc.gz
    │       │   ├── index.jsonlines
    │       │   └── manifest.json
    │       ├── gazettes
    │       │   ├── data.warc.gz
    │       │   ├── index.jsonlines
    │       │   └── manifest.json
    │       ├── legislation
    │       │   ├── data.warc.gz
    │       │   ├── index.jsonlines
    │       │   └── manifest.json
    │       └── outputs
    │           ├── zimlii_base_2022_04_29.tgz
    │           ├── zimlii_caselaw_2022_04_29.tgz
    │           ├── zimlii_gazettes_2022_04_29.tgz
    │           ├── zimlii_legislation_2022_04_29.tgz
    │           └── zimlii_packs.json
    ├── requirements.txt
    ├── warc_processor.py
    └── zimlii.warc
```

### Offline Search Index

To extract the search index from Elasticsearch:
1. Install `Logstash` by following [these instructions](https://www.elastic.co/guide/en/logstash/7.17/installing-logstash.html)
2. Install the required Logstash plugins:
    ```
    $ logstash-plugin install logstash-input-elasticsearch
    ```
3. Run the script with the required environment variables:
    ```
    $ cd search_index
    $ ES_HOST=localhost:9200 \
        ES_INDEX=peachjam \
        JSON_OUTPUT_DEST=./offline_search_index.json \
        ./make-search-index.sh
    ```
4. The resulting `offline_search_index.json` is ready for integration on Pocketlaw
