"""
@package ctiOS.csv
@brief Base abstract class creating the interface for ctiOS service

Classes:
 - ctiOS::CtiOSCsv

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import csv

from services.ctiOS import CtiOSBase
from services.ctiOS.csv.exceptions import CtiOSCsvError


class CtiOSCsv(CtiOSBase):
    """A concrete creator that implements concrete methods for CtiOSCsv class"""

    def __init__(self, username, password, csv_path):
        super().__init__(username, password)
        self.csv_path = csv_path

    def get_parameters_from_db(self, db_path):
        """Get posident array from db. Not defined for CtiOSCsv service."""
        raise NotImplementedError(self.__class__.__name__ + ".get_posidents_from_db")

    def write_output(self, dictionary):
        """Write output in the form of nested dictionary to csv."""
        if not dictionary:
            raise CtiOSCsvError(
                self.logger, "Writing to CSV failed! No values for output file."
            )

        # Write dictionary to csv
        header = sorted(set(i for b in map(dict.keys, dictionary.values()) for i in b))
        with open(self.csv_path, "w", newline="") as f:
            write = csv.writer(f)
            write.writerow(["posident", *header])
            for a, b in dictionary.items():
                write.writerow([a] + [b.get(i, "") for i in header])
                self.logger.info(
                        "Radky v csv u POSIdentu {} aktualizovany".format(a)
                )