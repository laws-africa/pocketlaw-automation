import argparse
import csv
import json
import logging
from os import path


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)-8s %(message)s",
                    datefmt="%d-%m-%Y %H:%M")
logger = logging.getLogger(__name__)

here = path.abspath(path.dirname(__file__))

parser = argparse.ArgumentParser(description="Process a CSV file into an offline search index JSON file")
parser.add_argument("--csv-input", required=True, help="location of the input CSV file")
parser.add_argument("--json-output", required=True, help="location of the output JSON file")

args = parser.parse_args()


def main():
    input_csv_path = path.join(here, args.csv_input)
    output_json_path = path.join(here, args.json_output)

    entries = []
    logger.info(f"Processing {input_csv_path} ...")
    with open(input_csv_path, 'r', newline='') as csv_input:
        csv_reader = csv.reader(csv_input, delimiter=',', quotechar='"')
        for ix, row in enumerate(csv_reader, start=1):
            entry = {
                "id": ix,
                "title": row[0] or None,
                "citation": row[1] or None,
                "url": row[2] or None,
                "date": row[3] or None,
                "type": row[4] or None
            }
            entries.append(entry)

    logger.info(f"Writing offline search index into {output_json_path} ...")
    with open(output_json_path, 'w') as json_output:
        json.dump(entries, json_output, indent=4)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Error processing {args.csv_input}: {str(e)}", exc_info=e)
        raise
