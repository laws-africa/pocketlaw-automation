import argparse
from datetime import datetime
import json
import logging
from os import path, makedirs
import shutil
import tarfile

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

PRODUCT = args.product
S3_URL = f"https://pocketlaw.s3.eu-west-1.amazonaws.com/{PRODUCT}/content-packs"
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
        "description": "This is the base content pack"
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
        "description": "This is the caselaw content pack",
        "baseUrl": "https://media.zimlii.org/files/judgments/"
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
        "description": "This is the gazettes content pack",
        "baseUrl": "https://media.zimlii.org/files/government_gazette/"
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
        "description": "This is the legislation content pack",
        "baseUrl": "https://media.zimlii.org/files/legislation/"
    },
}


class CustomIndexer(Indexer):
    """ Override warcio.Indexer.get_field() to output the following fields as ints instead of str:
        - offset
        - length
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

    def process_archive(self):
        self.setup()
        self.generate_data()
        self.generate_indexes()
        self.generate_manifest()
        self.generate_packs()
        self.upload_to_s3()
        self.update_packs_json()

    def setup(self):
        """ Create files folder and content packs folders within it.

        If any of these folders exists, delete them and recreate them.
        """
        # create files folder
        self.files_folder = path.join(here, 'files')
        if path.exists(self.files_folder):
            shutil.rmtree(self.files_folder)

        makedirs(self.files_folder)

        # create the pack sub_folders
        for pack_id in CONTENT_PACKS.keys():
            pack_folder = path.join(here, f'files/{pack_id}')
            if path.exists(pack_folder):
                shutil.rmtree(pack_folder)

            makedirs(pack_folder)

    def generate_data(self):
        """ Split the full warc archive into content pack data.warc.gz
        """
        base_writer = WARCWriter(filebuf=open(path.join(here, "files/base/data.warc.gz"), "wb"), gzip=True)
        caselaw_writer = WARCWriter(filebuf=open(path.join(here, "files/caselaw/data.warc.gz"), "wb"), gzip=True)
        gazettes_writer = WARCWriter(filebuf=open(path.join(here, "files/gazettes/data.warc.gz"), "wb"), gzip=True)
        legislation_writer = WARCWriter(filebuf=open(path.join(here, "files/legislation/data.warc.gz"), "wb"), gzip=True)

        with open(path.join(here, self.full_warc), "rb") as full_archive:
            for record in ArchiveIterator(full_archive, no_record_parse=False):
                record_uri = record.rec_headers.get_header("WARC-Target-URI")

                if record_uri and record_uri.startswith(f"https://media.{PRODUCT}.org/files/government_gazette/"):
                    gazettes_writer.write_record(record)
                elif record_uri and record_uri.startswith(f"https://media.{PRODUCT}.org/files/judgments/"):
                    caselaw_writer.write_record(record)
                elif record_uri and record_uri.startswith(f"https://media.{PRODUCT}.org/files/legislation/"):
                    legislation_writer.write_record(record)
                else:
                    base_writer.write_record(record)

    def generate_indexes(self):
        """ Generate index.jsonlines for each pack
        """
        fields = ['warc-type', 'warc-target-uri', 'offset', 'length']
        for pack_id in CONTENT_PACKS.keys():
            data_path = path.join(here, f'files/{pack_id}/data.warc.gz')
            index_path = path.join(here, f'files/{pack_id}/index.jsonlines')

            indexer = CustomIndexer(fields=fields, inputs=[data_path], output=index_path)
            indexer.process_all()

            log.info(f"{pack_id} indexed successfully")

    def generate_manifest(self):
        """ Generate manifest.json for each content pack
        """
        for pack_id, pack in CONTENT_PACKS.items():
            data_path = path.join(here, f'files/{pack_id}/data.warc.gz')
            manifest_path = path.join(here, f'files/{pack_id}/manifest.json')

            now = datetime.now()
            pack['date'] = now.isoformat()
            pack['dateString'] = now.strftime("%d %b, %Y")
            pack['size'] = path.getsize(data_path) 
            pack['sizeString'] = humanize.naturalsize(pack['size'])
            pack['version'] = now.strftime("%Y-%m-%d")
            pack['filename'] = f'{pack_id}_{now.strftime("%Y_%m_%d")}.tgz'
            pack['url'] = f"{S3_URL}/{pack['filename']}"

            with open(manifest_path, 'w') as manifest:
                json.dump(pack, manifest, indent=4)

    def generate_packs(self):
        """ Generate content_pack.tgz that contains data.warc.gz + index.jsonlines + manifest.json
        """
        for pack_id, pack in CONTENT_PACKS.items():
            content_pack_path = path.join(here, f"files/{pack['filename']}")
            files_path = path.join(here, f'files/{pack_id}/')

            with tarfile.open(content_pack_path, "w:gz") as tar:
                tar.add(files_path, arcname=path.basename(files_path))

    def upload_to_s3(self):
        """ Upload generated content pack to S3
        """
        pass

    def update_packs_json(self):
        """ Update pocketlaw-releases/PRODUCT/packs.json to reflect the new pack details
        """
        pass


if __name__ == '__main__':
    WarcProcessor(args.archive).process_archive()
