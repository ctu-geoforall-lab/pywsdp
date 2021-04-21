"""
(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""
import os
import sys
from ctios import CtiOsCsv

def main():
    user = "WSTEST"
    password = "WSHESLO"
    config_dir = os.path.join(os.path.abspath('ctios'), 'config', 'settings.ini')
    txt_path = os.path.join(os.path.abspath('ctios'), 'config', 'ctios.txt')
    csv_path = os.path.join(os.path.abspath('ctios'), 'ouput', 'ctios.csv')
    log_dir = os.path.join(os.path.abspath('ctios'), 'tests')
    ctios = CtiOsCsv(user, password, log_dir, config_dir, txt_path, csv_path)
    ids_array = ctios.get_posident_array()
    dictionary = ctios.getXMLresponse(ids_array)
    ctios.save_dictionary_to_csv(dictionary)

if __name__ == '__main__':
    sys.exit(main())