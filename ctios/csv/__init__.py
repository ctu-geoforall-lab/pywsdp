"""
@package ctios.csv
@brief Base abstract class creating the interface for CTIOS services

Classes:
 - ctios::CtiOsCsv
 - ctios::CsvManager

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""

import os
import csv

from ctios import CtiOs
from ctios.helpers import CtiOsCounter
from ctios.csv.exceptions import CtiOsCsvError



class CtiOsCsv(CtiOs):
    """A class that supposes the input as array and output in the form of csv."""

    def __init__(self, username, password, txt_path, config_path=None, out_dir=None, log_dir=None):
        super().__init__(username, password, config_path=None, out_dir=None, log_dir=None)
        self.logger.set_directory(self.log_dir)
        self.txt_path = txt_path
        self.csv_path = os.path.join(self.out_dir, 'ctios.csv')
        self.counter = CtiOsCounter()
        self.output_csv = CsvManager(self.csv_path)

    def _get_posident_array(self):
        """Get posident array from text file (delimiter is ',')."""
        with open(self.txt_path) as f:
            ids = f.read().split(',')
        ids_array = []
        for i in ids:
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i)
            ids_array.append(row)
        return ids_array

    def process(self):
        ids_array = self._get_posident_array()
        xml = self.renderXML(posidents=''.join(ids_array))
        response_xml = self.call_service(xml)
        dictionary = self.parseXML(response_xml, self.counter)
        print(dictionary)
        self.output_csv.write_dictionary_to_csv(dictionary, self.logger)


class CsvManager():
    """
    General WSDP class which writes parsed XML (dictionary) as csv
    """
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def write_dictionary_to_csv(self, dictionary, logger):
        """
        Write nested dictionary as csv

        Args:
            dictionary (nested dictonary): parsed  attributes
        """
        if not dictionary:
            raise CtiOsCsvError(logger, "Writing to CSV failed! No values for output file.")

        header = sorted(set(i for b in map(dict.keys, dictionary.values()) for i in b))
        with open(self.csv_path, 'w', newline="") as f:
          write = csv.writer(f)
          write.writerow(['posident', *header])
          for a, b in dictionary.items():
             write.writerow([a]+[b.get(i, '') for i in header])