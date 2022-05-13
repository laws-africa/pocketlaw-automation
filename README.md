# pocketlaw-automation

Script to automate generation of content packs

## Usage

To generate content packs from a `zimlii.warc` archive:

```bash
$ python warc_processor.py --product zimlii --archive ./zimlii.warc
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

### Docker

Generating and uploading content packs in Docker:
```
$ docker build \ 
    --build-arg PRODUCT_DOMAIN="zimlii.org" \
    --build-arg PRODUCT="zimlii" \
    --build-arg AWS_REGION="eu-west-1" \
    --build-arg AWS_KEY="<YOUR_AWS_CLI_KEY>" \
    --build-arg AWS_SECRET="<YOUR_AWS_CLI_SECRET>" \
    -t pl-extraction . \
    && docker run -d pl-extraction
```
