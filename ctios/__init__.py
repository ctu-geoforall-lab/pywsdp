"""
@package ctios
@brief Base abstract class creating the interface for CTIOS services

Classes:
 - ctios::CtiOsGdal
 - ctios::CtiOsCsv
 - ctios::CtiOsGdalManager
 - ctios::CtiOsCsvManager

(C) 2021 Linda Kladivova l.kladivova@seznam.cz
This library is free under the GNU General Public License.
"""

import csv
import sqlite3
from pathlib import Path

from ctios.base import CtiOs
from helpers import CtiOsConverter
from exceptions import CtiOsError, CtiOsGdalError, CtiOsInfo
from pywsdp.helpers import WSDPCsvManager



class CtiOsGdal(CtiOs):
    """A class that completed VFK db by adding all personal data."""

    def __init__(self, user, password, log_dir, config_dir, db_path, sql=None):
        super().__init__(user, password, log_dir, config_dir)
        self.db_path = db_path

        # Connection to db
        self.db = CtiOsGdalManager(db_path)
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


class CtiOsCsv(CtiOs):
    """A class that supposes the input as array and output in the form of csv."""

    def __init__(self, user, password, log_dir, config_dir, txt_path, csv_path):
        super().__init__(user, password, log_dir, config_dir)
        self.txt_path = txt_path
        self.csv_path = csv_path

    def get_posident_array(self):
        """Get posident array from text file (delimiter is ',')."""
        with open(self.txt_path) as f:
            ids_array = f.read().split(',')
        return ids_array

    def save_dictionary_to_csv(self, dictionary):
        """Save personal data to CSV"""
        output_csv = WSDPCsvManager(self.csv_path)
        output_csv.write_dictionary_to_csv(dictionary)


class CtiOsGdalManager:
    """
    CTIOS class for managing VFK SQLite database created based on Gdal
    """
    def __init__(self, db_path):
        self.conn = self._create_connection()
        self.cursor = self.conn.cursor()
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
            raise CtiOsError(e)

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
            raise CtiOsGdalError(e)

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
            raise CtiOsGdalError(e)

        # Control if not empty
        if len(ids) <= 1:
            msg = "Query has an empty result!"
            raise CtiOsGdalError(msg)
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
            raise CtiOsGdalError(e)
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
            raise CtiOsGdalError(e)

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
                CtiOsInfo('Radky v databazi u POSIdentu {} aktualizovany'.format(posident_id))
        except self.conn.Error as e:
            self.execute("ROLLBACK TRANSACTION")
            self.close(commit=True)
            raise CtiOsGdalError("Transaction Failed!: {}".format(e))
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
    def __init__(self, csv_dir):
        self.csv_dir = csv_dir

    def write_dictionary_to_csv(self, dictionary):
        """
        Write nested dictionary as csv

        Args:
            dictionary (nested dictonary): parsed  attributes
        """
        with open (self.csv_dir) as csv_file:
            writer = csv.writer(csv_file)
            fields = dictionary.values()[0].keys()
            for key in dictionary.keys():
                writer.writerow([key] + [dictionary[key][field] for field in fields])