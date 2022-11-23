import csv
import json
from os import path


# TODO: Logging

here = path.abspath(path.dirname(__file__))
input_csv_path = path.join(here, 'csv-export.csv')
output_json_path = path.join(here, 'offline_search_index.json')


def main():
    entries = []
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

    with open(output_json_path, 'w') as json_output:
        json.dump(entries, json_output)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
