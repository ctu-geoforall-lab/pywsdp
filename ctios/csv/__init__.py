"""
@package ctios.csv
@brief Base abstract class creating the interface for CTIOS services

Classes:
 - ctios::CtiOsCsv

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""

import os
import csv

from ctios import CtiOsBase

from ctios.exceptions import CtiOsInfo
from ctios.csv.exceptions import CtiOsCsvError


class CtiOsCsv(CtiOsBase):
    """A concrete creator that implements concrete methods for CtiOsCsv class"""

    def __init__(self, username, password, txt_path, config_path=None, out_dir=None, log_dir=None):
        super().__init__(username, password, config_path=None, out_dir=None, log_dir=None)
        self.txt_path = txt_path
        self.csv_path = os.path.join(self.out_dir, 'ctios.csv')

    def get_input(self):
        """Get posident array from text file (delimiter is ',')."""
        with open(self.txt_path) as f:
            ids = f.read().split(',')
        ids_array = []
        for i in ids:
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i)
            ids_array.append(row)
        return ids_array

    def create_output(self):
        with open (self.csv_path, 'w'):
            pass

    def write_output(self, dictionary):
        if not dictionary:
            raise CtiOsCsvError(self.logger, "Writing to CSV failed! No values for output file.")
        # Write dictionary to csv
        header = sorted(set(i for b in map(dict.keys, dictionary.values()) for i in b))
        with open(self.csv_path, 'w', newline="") as f:
          write = csv.writer(f)
          write.writerow(['posident', *header])
          for a, b in dictionary.items():
             write.writerow([a]+[b.get(i, '') for i in header])
             CtiOsInfo(self.logger, 'Radky v csv u POSIdentu {} aktualizovany'.format(a))
