"""
(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""
import os
import sys
from pywsdp.ctios import CtiOsGdal

def main():
    username = "WSTEST"
    password = "WSHESLO"
    config_path = os.path.join(os.path.abspath('ctios'), 'config', 'settings.ini')
    db_path = os.path.join(os.path.abspath('tests'), 'input_data', 'ctios.db')
    db_path_out = os.path.join(os.path.abspath('tests'), 'output_data', 'ctios.db')
    log_dir = os.path.join(os.path.abspath('tests'))
    ctios = CtiOsGdal(username, password, config_dir, db_path_in, db_path_out, log_dir)
    ids_array = ctios.get_posident_array()
    dictionary = ctios.getXMLresponse(ids_array)
    ctios.save_dictionary_to_db(dictionary)
username, password, db_path, sql=None, config_path=None, log_dir=None
#    ctios = CtiOsCsv(username=username,
#                     password=password,
#                     txt_path=txt_path,
#                     csv_path=csv_path)
#    ctios = CtiOsCsv(username=username,
#                     password=password,
#                     txt_path=txt_path,
#                     csv_path=csv_path,
#                     log_dir=log_dir)
    ctios = CtiOsCsv(username=username,
                     password=password,
                     txt_path=txt_path,
                     csv_path=csv_path,
                     config_path=config_path,
                     log_dir=log_dir)
    ids_array = ctios.get_posident_array()
    dictionary = ctios.getXMLresponse(ids_array)
    ctios.save_dictionary_to_csv(dictionary)
    
if __name__ == '__main__':
    sys.exit(main())