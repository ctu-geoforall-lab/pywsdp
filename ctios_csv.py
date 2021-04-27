"""
(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""
import os
import sys
from ctios import CtiOsCsv

def main():
    username = "WSTEST"
    password = "WSHESLO"
    config_path = os.path.join(os.path.abspath('ctios'), 'config', 'settings.ini')
    txt_path = os.path.join(os.path.abspath('tests'), 'input_data', 'ctios.txt')
    out_dir = os.path.join(os.path.abspath('tests'), 'output_data')
    log_dir = os.path.join(os.path.abspath('tests'))

    ctios = CtiOsCsv(username=username,
                     password=password,
                     txt_path=txt_path)

    ids_array = ctios.get_posident_array()
    dictionary = ctios.getXMLresponse(ids_array)
    ctios.save_dictionary_to_csv(dictionary)

#    ctios = CtiOsCsv(username=username,
#                     password=password,
#                     txt_path=txt_path,
#                     csv_path=csv_path)
#    ctios = CtiOsCsv(username=username,
#                     password=password,
#                     txt_path=txt_path,
#                     csv_path=csv_path,
#                     log_dir=log_dir)

if __name__ == '__main__':
    sys.exit(main())