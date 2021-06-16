"""
@package ctios.gdal
@brief Base abstract class creating the interface for CTIOS services

Classes:
 - ctios::CtiOsGdal
 - ctios::DbManager

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""


import os
import sqlite3
from pathlib import Path

from ctios import CtiOsBase
from ctios.gdal.converter import Xml2DbConverter

from ctios.exceptions import CtiOsError, CtiOsInfo
from ctios.gdal.exceptions import CtiOsGdalError



class CtiOsGdal(CtiOsBase):
    """A concrete creator that implements concrete methods for CtiOsGdal class"""

    def __init__(self, username, password, db_path):
        super().__init__(username, password)
        self.db_path = db_path
        self.db = DbManager(self.db_path, self.logger)

    def get_posidents_from_db(self, sql=None):
        """Get posident array from db."""
        with self.db._create_connection() as conn:
            return self.db.get_ids_array_from_db(conn, sql)

    def write_output(self, dictionary):
        """Write requested values to output database"""
        # Load mapping xml to db attributes csv
        mapping_attributes_path = os.path.join(os.path.abspath(self.get_service_name()),
                             'gdal',
                             'attributes_mapping.csv')
        # Save personal data to VFK db
        with self.db._create_connection() as conn:
            schema = "OPSUB"
            self.db.add_column_to_db(conn, schema, "OS_ID", "text")
            columns = self.db.get_columns_names(conn, schema) # for check
            dictionary = Xml2DbConverter(mapping_attributes_path, self.logger).convert_attributes(columns, dictionary)
            self.db.save_attributes_to_db(conn, schema, dictionary)


class DbManager():
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
            sql = "SELECT ID FROM OPSUB ORDER BY ID"
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

    def save_attributes_to_db(self, conn, schema, dictionary):
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
