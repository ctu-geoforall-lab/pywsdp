"""
testovani

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""
import os
import sys
from pywsdp.ctios import CtiOsDb
from pywsdp.ctios import CtiOsCsv

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
    user = "WSTEST"
    password = "WSHESLO"
    config_dir = os.path.join(os.path.abspath('ctios'), 'settings.ini')
    db_path = os.path.join(os.path.abspath('ctios'), 'ctios.db')
    log_dir = os.path.join(os.path.abspath('ctios'), 'tests')
    ctios = CtiOsDb(user, password, log_dir, config_dir, db_path)
    ids_array = ctios.get_posident_array()
    dictionary = ctios.getXMLresponse(ids_array)
    ctios.save_dictionary_to_db(dictionary)

if __name__ == '__main__':
    sys.exit(main())