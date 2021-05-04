"""
(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""
import os
import sys
from ctios.gdal import CtiOsGdal

def main():
    username = "WSTEST"
    password = "WSHESLO"
    db_path = os.path.join(os.path.abspath('tests'), 'input_data', 'Export_1-4.db')
    config_path = os.path.join(os.path.abspath('ctios'), 'config', 'settings.ini')
    out_dir = os.path.join(os.path.abspath('tests'), 'output_data')
    log_dir = os.path.join(os.path.abspath('tests'), 'ctios')
    sql="SELECT ID FROM OPSUB LIMIT 10"

    ctios = CtiOsGdal(username=username,
              password=password,
              db_path=db_path,
              sql=sql)
    ctios.process()

#    ctios = CtiOsGdal(username=username,
#                      password=password,
#                      config_dir=config_dir,
#                      db_path=db_path,
#                      out_dir=out_dir,
#                      log_dir=log_dir)

if __name__ == '__main__':
    sys.exit(main())