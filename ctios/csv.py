"""
@package ctios
@brief A result class processing input posidents from text file to output csv containing all personal data

Classes:
 - ctios::CtiOsCsv

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""


import os
import sys

from base.core import CtiOs
from base.helpers import WSDPCsvManager



class CtiOsCsv(CtiOs):
    """A class that supposes the input as array and output in the form of csv."""

    def __init__(self, user, password, log_dir, config_dir, txt_path, csv_path):
        super().__init__(user, password, log_dir, config_dir)
        self.txt_path = txt_path
        self.csv_path = csv_path

    def get_posident_array(self):
        """Get posident array from text file (delimiter is ',')."""
        with open(self.txt_path) as f:
            ids_array = f.read().split(',')
        return ids_array

    def save_dictionary_to_csv(self, dictionary):
        """Save personal data to CSV"""
        output_csv = WSDPCsvManager(self.csv_path)
        output_csv.write_dictionary_to_csv(dictionary)


def main():
    user = "WSTEST"
    password = "WSHESLO"
    config_dir = os.path.join(os.path.abspath('ctios'), 'settings', 'settings.ini')
    txt_path = os.path.join(os.path.abspath('ctios'), 'ctios.txt')
    csv_path = os.path.join(os.path.abspath('ctios'), 'ctios.csv')
    log_dir = os.path.join(os.path.abspath('ctios'), 'tests')
    ctios = CtiOsCsv(user, password, log_dir, config_dir, txt_path, csv_path)
    ids_array = ctios.get_posident_array()
    dictionary = ctios.getXMLresponse(ids_array)
    ctios.save_dictionary_to_csv(dictionary)


if __name__ == '__main__':
    sys.exit(main())