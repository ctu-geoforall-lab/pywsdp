"""
@package ctios
@brief A result class processing VFK db rows and adding all personal data

Classes:
 - ctios::CtiOsDb

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""


import os

from pywsdp.ctios import CtiOs
from ctios.base import CtiOsConverter, CtiOsDbManager



class CtiOsDb(CtiOs):
    """A class that completed VFK db by adding all personal data."""

    def __init__(self, user, password, log_dir, config_dir, db_path, sql=None):
        super().__init__(user, password, log_dir, config_dir)
        self.db_path = db_path

        # Connection to db
        self.db = CtiOsDbManager(db_path)
        # XML to DB converter
        self.converter = CtiOsConverter()

        self.schema = "OPSUB"

    def get_posident_array(self, sql):
        """Get posident array from db."""
        ids = self.db.get_ids(sql)
        ids_array = []
        for i in ids:
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i[0])
            ids_array.append(row)
        return ids_array

    def save_dictionary_to_db(self, dictionary):
        """Save personal data to VFK db"""
        self.db.add_column_to_db(self.schema, "OS_ID", "text")
        columns = self.db.get_columns_names(self.schema)
        dictionary = CtiOsConverter(dictionary).convert_attributes(columns)
        self.db.save_attributes_to_db(self.schema, dictionary, self.counter)


if __name__ == '__main__':
    user = "WSTEST"
    password = "WSHESLO"
    config_dir = os.path.join(os.path.abspath('ctios'), 'settings.ini')
    db_path = os.path.join(os.path.abspath('ctios'), 'ctios.db')
    log_dir = os.path.join(os.path.abspath('ctios'), 'tests')
    ctios = CtiOsDb(user, password, log_dir, config_dir, db_path)
    ids_array = ctios.get_posident_array()
    dictionary = ctios.getXMLresponse(ids_array)
    ctios.save_dictionary_to_db(dictionary)