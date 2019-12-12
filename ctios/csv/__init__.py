import csv
import os

class CtiOsCsv:
    def __init__(self, CSV_DIR):
        if CSV_DIR and os.path.isabs(CSV_DIR):
            self.CSV_DIR = CSV_DIR
        else:
            # relative paths are not supported
            self.CSV_DIR = os.path.join(
                os.path.dirname(__file__)
            )

    def read_csv_as_dictionary(self, csv_path):
        dictionary = {}
        with open(os.path.join(self.CSV_DIR, csv_path)) as csv_file:
            rows = csv.reader(csv_file, delimiter=';')
            for row in rows:
                [k, v, l] = row
                dictionary[k] = v
            return dictionary
