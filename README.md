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
