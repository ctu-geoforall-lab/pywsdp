"""
@package ctios.core
@brief Base abstract class creating the interface for CTIOS services

Classes:
 - ctios::CtiOsGdal
 - ctios::CtiOsCsv
 - ctios::CtiOsGdalManager
 - ctios::CtiOsCsvManager

(C) 2021 Linda Kladivova l.kladivova@seznam.cz
This library is free under the GNU General Public License.
"""

import os
import csv
import sqlite3
import shutil
from pathlib import Path

from ctios.core import CtiOs
from ctios.helpers import CtiOsConverter, CtiOsCounter
from ctios.exceptions import CtiOsError, CtiOsGdalError, CtiOsCsvError, CtiOsInfo



class CtiOsGdal(CtiOs):
    """A class that completed VFK db by adding all personal data."""

    def __init__(self, username, password, db_path, sql=None, config_path=None, out_dir=None, log_dir=None):
        super().__init__(username, password, config_path=None, out_dir=None, log_dir=None)
        self.logger.set_directory(self.log_dir)
        self.db_path = db_path
        self.sql = sql
        self.counter = CtiOsCounter()

        # Copy input db to out dir
        input_dir, db_name = os.path.split(self.db_path)
        db_out_path = os.path.join(self.out_dir, db_name)
        shutil.copyfile(self.db_path, db_out_path)

        self.db = CtiOsGdalManager(db_out_path, self.logger)

    def _get_posident_array(self, sql=None):
        """Get posident array from db."""
        with self.db._create_connection() as conn:
            ids_array = self.db.get_ids_array_from_db(conn, sql)
        return ids_array

    def process(self):
        schema = "OPSUB"
        mapping_attributes_path = os.path.join(os.path.abspath(self.get_service_name()),
                                     'config',
                                     'attributes_mapping.csv')
        print(mapping_attributes_path)

        ids_array = self._get_posident_array(self.sql)
        xml = self.renderXML(posidents=''.join(ids_array))
        response_xml = self.call_service(xml)
        dictionary = self.parseXML(response_xml, self.counter)
        print(dictionary)

        # Save personal data to VFK db
        with self.db._create_connection() as conn:
            self.db.add_column_to_db(conn, schema, "OS_ID", "text")
            columns = self.db.get_columns_names(conn, schema)
            print(columns)
            dictionary = CtiOsConverter(dictionary, mapping_attributes_path, self.logger).convert_attributes(columns)
            self.db.save_attributes_to_db(conn, schema, dictionary, self.counter)


class CtiOsCsv(CtiOs):
    """A class that supposes the input as array and output in the form of csv."""

    def __init__(self, username, password, txt_path, config_path=None, out_dir=None, log_dir=None):
        super().__init__(username, password, config_path=None, out_dir=None, log_dir=None)
        self.logger.set_directory(self.log_dir)
        self.txt_path = txt_path
        self.csv_path = os.path.join(self.out_dir, 'ctios.csv')
        self.counter = CtiOsCounter()
        self.output_csv = CtiOsCsvManager(self.csv_path)

    def _get_posident_array(self):
        """Get posident array from text file (delimiter is ',')."""
        with open(self.txt_path) as f:
            ids = f.read().split(',')
        ids_array = []
        for i in ids:
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i)
            ids_array.append(row)
        return ids_array

    def process(self):
        ids_array = self._get_posident_array()
        xml = self.renderXML(posidents=''.join(ids_array))
        response_xml = self.call_service(xml)
        dictionary = self.parseXML(response_xml, self.counter)
        print(dictionary)
        self.output_csv.write_dictionary_to_csv(dictionary, self.logger)


class CtiOsGdalManager():
    """
    CTIOS class for managing VFK SQLite database created based on Gdal
    """
    def __init__(self, db_path, logger):
        self.logger = logger
        self.db_path = self._check_db(db_path)

    def _check_db(self, db_path):
        """
        Control path to db
        Args:
            db_path (str): Path to vfk db
        Raises:
            CtiOsError: FileNotFoundError
        """
        my_file = Path(db_path)
        try:
            # Control if database file exists
            my_file.resolve(strict=True)
            return db_path

        except FileNotFoundError as e:
            raise CtiOsError(self.logger, e)

    def _create_connection(self):
        """
        Create a database connection to the SQLite database specified by the db_path
        Raises:
            CtiOsGdalError: SQLite error
        Returns:
            conn (Connection object)
        """

        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            raise CtiOsGdalError(self.logger, e)

    def get_ids_array_from_db(self, conn, sql=None):
        """
        Get ids from db
        Args:
            conn (Connection object)
            sql (str): SQL select statement for filtering or None (if not specified, all ids from db are selected)
        Raises:
            CtiOsGdalError: SQLite error (Raises when not possible to connect to db)
            CtiOsGdalError: Query has an empty result! (Raises when the response is empty)
        Returns:
            ids_array (list): pseudo ids from db
        """
        if not sql:
            sql = "SELECT ID FROM OPSUB"
        try:
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            ids = cur.fetchall()
        except sqlite3.Error as e:
            raise CtiOsGdalError(self.logger, e)

        # Control if not empty
        if len(ids) <= 1:
            msg = "Query has an empty result!"
            raise CtiOsGdalError(self.logger, msg)

        ids_array = []
        for i in list(set(ids)):
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i[0])
            ids_array.append(row)

        return ids_array

    def get_columns_names(self, conn, schema):
        """
        Get names of columns in schema
        Args:
            conn (Connection object)
            schema (str): name of schema in db
        Raises:
            CtiOsGdalError: SQLite error
         Returns:
             col_names (list): column names in given schema
        """
        try:
            cur = conn.cursor()
            cur.execute("PRAGMA read_committed = true;")
            cur.execute("""select * from {0}""".format(schema))
            col_names = list(map(lambda x: x[0], cur.description))
        except sqlite3.Error as e:
            raise CtiOsGdalError(self.logger, e)
        return col_names

    def add_column_to_db(self, conn, schema, name, datatype):
        """
        Add column to db
        Args:
            conn (Connection object)
            schema (str): name of schema in db
            name (str): name of column
            datatype (str): column data type
        Raises:
            CtiOsGdalError: SQLite error
        """
        col_names = self.get_columns_names(conn, schema)
        try:
            cur = conn.cursor()
            if name not in col_names:
                cur.execute("""ALTER TABLE {0} ADD COLUMN {1} {2}""".format(schema, name, datatype))
        except sqlite3.Error as e:
            raise CtiOsGdalError(self.logger, e)

    def save_attributes_to_db(self, conn, schema, dictionary, counter):
        """
        Save dictionary attributes to db
        Args:
            conn (Connection object)
            schema (str): name of schema in db
            dictionary (nested dictonary): converted DB attributes
            counter (class): class managing statistics info
        Raises:
            CtiOsGdalError: SQLite error
        """
        try:
            cur = conn.cursor()
            cur.execute("BEGIN TRANSACTION")
            for posident_id, posident_info in dictionary.items():
                #  Update table OPSUB by database attributes items
                for dat_name in posident_info:
                    cur.execute("""UPDATE OPSUB SET {0} = ? WHERE id = ?""".format(dat_name), (posident_info[dat_name], posident_id))
            cur.execute("COMMIT TRANSACTION")
            CtiOsInfo(self.logger, 'Radky v databazi u POSIdentu {} aktualizovany'.format(posident_id))
        except conn.Error as e:
            cur.execute("ROLLBACK TRANSACTION")
            cur.close()
            raise CtiOsGdalError(self.logger, "Transaction failed!: {}".format(e))


class CtiOsCsvManager():
    """
    General WSDP class which writes parsed XML (dictionary) as csv
    """
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def write_dictionary_to_csv(self, dictionary, logger):
        """
        Write nested dictionary as csv

        Args:
            dictionary (nested dictonary): parsed  attributes
        """
        if not dictionary:
            raise CtiOsCsvError(logger, "Writing to CSV failed! No values for output file.")

        header = sorted(set(i for b in map(dict.keys, dictionary.values()) for i in b))
        with open(self.csv_path, 'w', newline="") as f:
          write = csv.writer(f)
          write.writerow(['posident', *header])
          for a, b in dictionary.items():
             write.writerow([a]+[b.get(i, '') for i in header])