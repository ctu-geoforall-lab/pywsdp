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
from pathlib import Path

from ctios.core import CtiOs
from ctios.helpers import CtiOsConverter
from ctios.exceptions import CtiOsError, CtiOsGdalError, CtiOsCsvError, CtiOsInfo



class CtiOsGdal(CtiOs):
    """A class that completed VFK db by adding all personal data."""

    def __init__(self, username, password, db_path, sql=None, out_dir=None, config_path=None, log_dir=None):
        super().__init__(username, password, config_path=None)
        self.db_path = db_path
        if out_dir:
            self.out_dir = out_dir
        else:
            self.log_dir = self.get_default_out_dir()
        if log_dir:
            self.log_dir = log_dir
        else:
            self.log_dir = self.get_default_log_dir()
        self.logger.set_directory(self.log_dir)

        # Connection to db
        self.db = CtiOsGdalManager(db_path, self.logger)
        # XML to DB converter
        self.converter = CtiOsConverter(self.logger)

        self.schema = "OPSUB"

    def get_posident_array(self, sql):
        """Get posident array from db."""
        ids = self.db.get_ids(sql)
        ids_array = []
        for i in ids:
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i[0])
            ids_array.append(row)
        #print(ids_array)
        return ids_array

    def save_dictionary_to_db(self, dictionary):
        """Save personal data to VFK db"""
        self.db.add_column_to_db(self.schema, "OS_ID", "text")
        columns = self.db.get_columns_names(self.schema)
        dictionary = CtiOsConverter(dictionary).convert_attributes(columns)
        self.db.save_attributes_to_db(self.schema, dictionary, self.counter)


class CtiOsCsv(CtiOs):
    """A class that supposes the input as array and output in the form of csv."""

    def __init__(self, username, password, txt_path, out_dir=None, config_path=None, log_dir=None):
        super().__init__(username, password, config_path=None)
        self.txt_path = txt_path
        if out_dir:
            self.out_dir = out_dir
        else:
            self.out_dir = self.get_default_out_dir()
        self.csv_path = os.path.join(self.out_dir, 'ctios.csv')
        if log_dir:
            self.log_dir = log_dir
        else:
            self.log_dir = self.get_default_log_dir()
        self.logger.set_directory(self.log_dir)

    def get_posident_array(self):
        """Get posident array from text file (delimiter is ',')."""
        with open(self.txt_path) as f:
            ids = f.read().split(',')
        ids_array = []
        for i in ids:
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i)
            ids_array.append(row)
        return ids_array

    def save_dictionary_to_csv(self, dictionary):
        """Save personal data to CSV"""
        output_csv = CtiOsCsvManager(self.csv_path)
        output_csv.write_dictionary_to_csv(dictionary, self.logger)


class CtiOsGdalManager:
    """
    CTIOS class for managing VFK SQLite database created based on Gdal
    """
    def __init__(self, db_path, logger):
        self.conn = self._create_connection()
        self.cursor = self.conn.cursor()
        self.db_path = self._check_db(db_path)
        self.logger = logger

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
            CtiOsDbError(SQLite error)
        Returns:
            conn (Connection object)
        """

        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            raise CtiOsGdalError(self.logger, e)

    def get_ids_from_db(self, sql=None):
        """
        Get ids from db
        Args:
            sql (str): SQL select statement for filtering or None (if not specified, all ids from db are selected)
        Raises:
            CtiOsError: Query has an empty result! (Raises when the response is empty)
        Returns:
            ids (list): pseudo ids from db
        """
        if sql:
            sql = "SELECT ID FROM OPSUB"
        try:
            ids = self.query(sql)
            self.close()
        except sqlite3.Error as e:
            raise CtiOsGdalError(self.logger, e)

        # Control if not empty
        if len(ids) <= 1:
            msg = "Query has an empty result!"
            raise CtiOsGdalError(self.logger, msg)
        return ids

    def get_columns_names(self, schema):
        """
        Get names of columns in schema
        Args:
            schema (str): name of schema in db
        Raises:
            CtiOsDbError: "Database error"
        """
        try:
            self.cursor.execute("PRAGMA read_committed = true;")
            self.cursor.execute("""select * from {0}""".format(schema))
            col_names = list(map(lambda x: x[0], self.cursor.description))
            self.cursor.close()
        except sqlite3.Error as e:
            raise CtiOsGdalError(self.logger, e)
        return col_names

    def add_column_to_db(self, schema, name, datatype):
        """
        Add column to db
        Args:
            schema (str): name of schema in db
            name (str): name of column
            datatype (str): column data type
        Raises:
            CtiOsDbError: "Database error"
        """
        col_names = self.get_columns_names(schema)
        try:
            if name not in col_names:
                self.cursor.execute("""ALTER TABLE {0} ADD COLUMN {1} {2}""".format(schema, name, datatype))
            self.cursor.close()
        except sqlite3.Error as e:
            raise CtiOsGdalError(self.logger, e)

    def save_attributes_to_db(self, schema, dictionary, counter):
        """
        Save dictionary attributes to db
        Args:
            schema (str): name of schema in db
            dictionary (nested dictonary): converted DB attributes
        Raises:
            CtiOsDbError: "Database error"
        """
        try:
            self.execute("BEGIN TRANSACTION")
            for posident_id, posident_info in dictionary.items():
                #  Update table OPSUB by database attributes items
                for dat_name in posident_info:
                    self.execute("""UPDATE OPSUB SET {0} = ? WHERE id = ?""".format(dat_name), (posident_info[dat_name], posident_id))
                self.execute("COMMIT TRANSACTION")
                self.cursor.close()
                CtiOsInfo(self.logger, 'Radky v databazi u POSIdentu {} aktualizovany'.format(posident_id))
        except self.conn.Error as e:
            self.execute("ROLLBACK TRANSACTION")
            self.close(commit=True)
            raise CtiOsGdalError(self.logger, "Transaction failed!: {}".format(e))
        finally:
            self.counter.add_uspesne_stazeno()
            if self.conn:
                self.conn.close()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.cursor.close()
        self.conn.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()


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