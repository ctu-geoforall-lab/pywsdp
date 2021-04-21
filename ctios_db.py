"""
(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""
import os
import sys
from pywsdp.ctios import CtiOsGdal

def main():
    user = "WSTEST"
    password = "WSHESLO"
    config_dir = os.path.join(os.path.abspath('ctios'), 'settings.ini')
    db_path = os.path.join(os.path.abspath('ctios'), 'ctios.db')
    log_dir = os.path.join(os.path.abspath('ctios'), 'tests')
    ctios = CtiOsGdal(user, password, log_dir, config_dir, db_path)
    ids_array = ctios.get_posident_array()
    dictionary = ctios.getXMLresponse(ids_array)
    ctios.save_dictionary_to_db(dictionary)

if __name__ == '__main__':
    sys.exit(main())