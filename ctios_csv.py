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
    log_dir = os.path.join(os.path.abspath('tests'), 'ctios')

#    ctios = CtiOsCsv(username=username,
#             password=password,
#             txt_path=txt_path)
#    ctios = CtiOsCsv(username=username,
#                     password=password,
#                     txt_path=txt_path,
#                     config_path=config_path)
    ctios = CtiOsCsv(username=username,
                     password=password,
                     txt_path=txt_path,
                     config_path=config_path,
                     out_dir=out_dir,
                     log_dir=log_dir)
    ctios.process()



if __name__ == '__main__':
    sys.exit(main())