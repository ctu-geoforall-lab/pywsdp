###############################################################################
# Name:         CtiOSParser
# Purpose:      Connects db and save attributes to db
# Date:         March 2021
# Copyright:    (C) 2021 Linda Kladivova
# Email:        l.kladivova@seznam.cz
###############################################################################

from pathlib import Path
import sqlite3

from ctios.messages import CtiOsError, CtiOsInfo


class CtiOsDbError(CtiOsError):
    """Basic exception for errors raised by db"""
    def __init__(self, msg):
        super(CtiOsDbError, self).__init__('{} - {}'.format('SQLite3 ERROR', msg))


class CtiOsDb():
    """
        CtiOsDb class contains methods for connecting to VFK db and savinf attributes to db
    """
    def __init__(self, db_path, stats):
        self.db_path = self._set_db(db_path)
        self.conn = self._create_connection()
        self.stats = stats

    def _set_db(self, db_path):
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
        Create a database connection to the SQLite database specified by the db_file

        Raises:
            CtiOsDbError(SQLite error)

        Returns:
            conn (Connection object)
        """

        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            raise CtiOsDbError(e)

    def get_ids_from_db(self, schema, sql=None):
        """
        Get ids from db

        Args:
            schema (str): name of schema in db
            sql (str): SQL select statement for filtering or None (if not specified, all ids from db are selected)

        Raises:
            CtiOsError: Query has an empty result! (Raises when the response is empty)

        Returns:
            ids (list): pseudo ids from db
        """

        if sql is None:
            sql = "SELECT ID FROM {0}".format(schema)
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            ids = cur.fetchall()
            ids = list(set(ids))
            cur.close()
        except sqlite3.Error as e:
            raise CtiOsDbError(e)

        # Control if not empty
        if len(ids) <= 1:
            msg = "Query has an empty result!"
            raise CtiOsError(msg)
        return ids

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
        try:
            cur = self.conn.cursor()
            cur.execute("PRAGMA read_committed = true;")
            cur.execute("""select * from {0}""".format(schema))
            col_names = list(map(lambda x: x[0], cur.description))
            if name not in col_names:
                cur.execute("""ALTER TABLE {0} ADD COLUMN {1} {2}""".format(schema, name, datatype))
            cur.close()
        except sqlite3.Error as e:
            raise CtiOsDbError(e)

    def get_columns_names(self, schema):
        """
        Get names of columns in schema

        Args:
            schema (str): name of schema in db

        Raises:
            CtiOsDbError: "Database error"
        """
        try:
            cur = self.conn.cursor()
            cur.execute("PRAGMA read_committed = true;")
            cur.execute("""select * from {0}""".format(schema))
            col_names = list(map(lambda x: x[0], cur.description))
            cur.close()
        except sqlite3.Error as e:
            raise CtiOsDbError(e)
        return col_names

    def save_attributes_to_db(self, schema, dictionary):
        """
        Save dictionary attributes to db

        Args:
            schema (str): name of schema in db
            dictionary (nested dictonary): converted DB attributes

        Raises:
            CtiOsDbError: "Database error"
        """
        try:
            cur = self.conn.cursor()
            cur.execute("BEGIN TRANSACTION")
            for posident_id, posident_info in dictionary.items():
                #  Update table OPSUB by database attributes items
                for dat_name in posident_info:
                    cur.execute("""UPDATE OPSUB SET {0} = ? WHERE id = ?""".format(dat_name), (posident_info[dat_name], posident_id))
                cur.execute("COMMIT TRANSACTION")
                cur.close()
                CtiOsInfo('Radky v databazi u POSIdentu {} aktualizovany'.format(posident_id))
        except self.conn.Error as e:
            cur.execute("ROLLBACK TRANSACTION")
            cur.close()
            self.conn.close()
            raise CtiOsDbError("Transaction Failed!: {}".format(e))
        finally:
            self.stats.add_uspesne_stazeno()
            if self.conn:
                self.conn.close()
