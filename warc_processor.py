import argparse
from datetime import datetime
import json
import logging
from os import path, makedirs
import shutil
import tarfile

import boto3
import humanize
from warcio.indexer import Indexer
from warcio.warcwriter import WARCWriter
from warcio.archiveiterator import ArchiveIterator


here = path.abspath(path.dirname(__file__))
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Process a warc archive file into content packs.")
parser.add_argument("--product", required=True, help="the LII website e.g. zimlii, namiblii")
parser.add_argument("--archive", required=True, help="location of the warc archive file")

args = parser.parse_args()

PRODUCT = args.product.lower()
CONTENT_PACKS = {
    "base": {
        "id": "base",
        "name": "Base Pack",
        "url": None,
        "size": None,
        "sizeString": None,
        "version": None,
        "date": None,
        "dateString": None,
        "filename": None,
        "description": "This is the base content pack that contains all the content except for document files (PDF, DOCX, RTF e.t.c) - these files are included in the other content packs."
    },
    "caselaw": {
        "id": "caselaw",
        "name": "Caselaw",
        "url": None,
        "size": None,
        "sizeString": None,
        "version": None,
        "date": None,
        "dateString": None,
        "filename": None,
        "description": "This is the content pack that contains the document files (PDF, DOCX, RTF e.t.c) for caselaw content.",
        "baseUrl": f"https://media.{PRODUCT}.org/files/judgments/"
    },
    "gazettes": {
        "id": "gazettes",
        "name": "Gazettes",
        "url": None,
        "size": None,
        "sizeString": None,
        "version": None,
        "date": None,
        "dateString": None,
        "filename": None,
        "description": "This is the content pack that contains the document files (PDF, DOCX, RTF e.t.c) for gazettes content.",
        "baseUrl": f"https://media.{PRODUCT}.org/files/government_gazette/"
    },
    "legislation": {
        "id": "legislation",
        "name": "Legislation",
        "url": None,
        "size": None,
        "sizeString": None,
        "version": None,
        "date": None,
        "dateString": None,
        "filename": None,
        "description": "This is the content pack that contains the document files (PDF, DOCX, RTF e.t.c) for legislation content.",
        "baseUrl": f"https://media.{PRODUCT}.org/files/legislation/"
    },
}


class CustomIndexer(Indexer):
    """ Override warcio.Indexer.get_field() to output the following fields as ints instead of str:
        - offset
        - length

    Original: https://github.com/webrecorder/warcio/blob/aa702cb321621b233c6e5d2a4780151282a778be/warcio/indexer.py#L64
    """

    def get_field(self, record, name, it, filename):
        value = None
        if name == 'offset':
            value = it.get_record_offset()
        elif name == 'length':
            value = it.get_record_length()
        elif name == 'filename':
            value = path.basename(filename)
        elif name == 'http:status':
            if record.rec_type in ('response', 'revisit') and record.http_headers:
                value = record.http_headers.get_statuscode()
        elif name.startswith('http:'):
            if record.http_headers:
                value = record.http_headers.get_header(name[5:])
        else:
            value = record.rec_headers.get_header(name)

        return value


# TODO: add logs for each step
# TODO: add exceptions
class WarcProcessor:
    def __init__(self, full_warc):
        self.full_warc = full_warc
        self.product = PRODUCT

        self.files_path = path.join(here, f'files/{self.product}')
        self.outputs_path = path.join(self.files_path, 'outputs')

        self.s3_resource = boto3.resource('s3')
        self.s3_client = boto3.client('s3')
        self.s3_bucket = self.s3_resource.Bucket('pocketlaw-test')
        # TODO: get region from bucket object via boto3
        self.s3_region = 'us-east-1'
        self.s3_base_url = f"https://{self.s3_bucket.name}.s3.{self.s3_region}.amazonaws.com/{self.product}"

    def process_archive(self):
        self.setup()
        self.generate_data()
        self.generate_indexes()
        self.generate_manifest()
        self.generate_packs()
        self.generate_packs_json()
        self.upload_to_s3()

    def setup(self):
        """ Create files folder and content packs & outputs folders within it.

        If any of these folders exists, delete them and recreate them.
        """
        # create files folder
        if path.exists(self.files_path):
            shutil.rmtree(self.files_path)

        makedirs(self.files_path)

        # create the pack sub_folders
        for pack_id in CONTENT_PACKS.keys():
            pack_folder = path.join(self.files_path, f'{pack_id}')
            if path.exists(pack_folder):
                shutil.rmtree(pack_folder)

            makedirs(pack_folder)

        # create outputs folder
        if path.exists(self.outputs_path):
            shutil.rmtree(self.outputs_path)

        makedirs(self.outputs_path)

    def generate_data(self):
        """ Split the full warc archive into content pack data.warc.gz
        """
        # TODO: Make these writers dynamic
        base_writer = WARCWriter(filebuf=open(path.join(self.files_path, "base/data.warc.gz"), "wb"), gzip=True)
        caselaw_writer = WARCWriter(filebuf=open(path.join(self.files_path, "caselaw/data.warc.gz"), "wb"), gzip=True)
        gazettes_writer = WARCWriter(filebuf=open(path.join(self.files_path, "gazettes/data.warc.gz"), "wb"), gzip=True)
        legislation_writer = WARCWriter(filebuf=open(path.join(self.files_path, "legislation/data.warc.gz"), "wb"), gzip=True)

        with open(path.join(here, self.full_warc), "rb") as full_archive:
            for record in ArchiveIterator(full_archive, no_record_parse=False):
                record_uri = record.rec_headers.get_header("WARC-Target-URI")

                if record_uri and record_uri.startswith(f"https://media.{self.product}.org/files/government_gazette/"):
                    gazettes_writer.write_record(record)
                elif record_uri and record_uri.startswith(f"https://media.{self.product}.org/files/judgments/"):
                    caselaw_writer.write_record(record)
                elif record_uri and record_uri.startswith(f"https://media.{self.product}.org/files/legislation/"):
                    legislation_writer.write_record(record)
                else:
                    base_writer.write_record(record)

    def generate_indexes(self):
        """ Generate index.jsonlines for each pack
        """
        fields = ['warc-type', 'warc-target-uri', 'offset', 'length']
        for pack_id in CONTENT_PACKS.keys():
            data_path = path.join(self.files_path, f'{pack_id}/data.warc.gz')
            index_path = path.join(self.files_path, f'{pack_id}/index.jsonlines')

            indexer = CustomIndexer(fields=fields, inputs=[data_path], output=index_path)
            indexer.process_all()

            log.info(f"{pack_id} indexed successfully")

    def generate_manifest(self):
        """ Generate manifest.json for each content pack
        """
        for pack_id, pack in CONTENT_PACKS.items():
            data_path = path.join(self.files_path, f'{pack_id}/data.warc.gz')
            manifest_path = path.join(self.files_path, f'{pack_id}/manifest.json')

            now = datetime.now()
            pack['date'] = now.isoformat()
            pack['dateString'] = now.strftime("%d %b, %Y")
            pack['size'] = path.getsize(data_path)
            pack['sizeString'] = humanize.naturalsize(pack['size'])
            pack['version'] = now.strftime("%Y-%m-%d")
            pack['filename'] = f'{self.product}_{pack_id}_{now.strftime("%Y_%m_%d")}.tgz'
            pack['url'] = f"{self.s3_base_url}/content-packs/{pack['filename']}"

            with open(manifest_path, 'w') as manifest:
                json.dump(pack, manifest, indent=4)

    def generate_packs(self):
        """ Generate content_pack.tgz that contains data.warc.gz + index.jsonlines + manifest.json
        """
        for pack_id, pack in CONTENT_PACKS.items():
            content_pack_path = path.join(self.outputs_path, f"{pack['filename']}")
            files_path = path.join(self.files_path, f'{pack_id}')

            with tarfile.open(content_pack_path, "w:gz") as tar:
                tar.add(files_path, arcname=path.sep)

    def generate_packs_json(self):
        """ Update pocketlaw-releases/self.product/packs.json to reflect the new pack details
        """
        packs_json_path = path.join(self.outputs_path, f'{self.product}_packs.json')
        packs_json = {}

        for pack_id, pack in CONTENT_PACKS.items():
            packs_json[pack_id] = {
                "url": pack['url'],
                "filename": pack['filename'],
                "size": pack['size'],
                "sizeString": pack['sizeString'],
                "version": pack['version'],
                "date": pack['date'],
                "dateString": pack['dateString']
            }

        with open(packs_json_path, 'w') as manifest:
            json.dump(packs_json, manifest, indent=4)

    def upload_to_s3(self):
        """ Upload generated content pack to S3
        """
        # empty bucket
        # TODO: delete folder contents and keep fodler
        self.s3_bucket.objects.filter(Prefix=f'{self.product}/').delete()

        # upload content packs
        for pack_id, pack in CONTENT_PACKS.items():
            content_pack_path = path.join(self.outputs_path, f"{pack['filename']}")

            log.info(f"Uploading {pack_id} to s3...")
            with open(content_pack_path, 'rb') as data:
                self.s3_bucket.put_object(Key=f"{self.product}/content-packs/{pack['filename']}", Body=data)

            log.info(f"{pack_id} content pack uploaded to: {self.s3_base_url}/content-packs/{pack['filename']}")

        # upload packs_json
        packs_json_path = path.join(self.outputs_path, f'{self.product}_packs.json')
        with open(packs_json_path, 'rb') as data:
            self.s3_bucket.put_object(Key=f'{self.product}/{self.product}_packs.json', Body=data)

        log.info(f"{self.product}_packs.json uploaded to: {self.s3_base_url}/{self.product}_packs.json")


if __name__ == '__main__':
    WarcProcessor(args.archive).process_archive()
