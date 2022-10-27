"""
@package modules.helpers

@brief Helpers for CtiOs module

Classes:
 - helpers::AttributeConverter
 - helpers::DbManager

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import re
import sqlite3
from pathlib import Path

from pywsdp.base.exceptions import WSDPError


class AttributeConverter:
    """
    CtiOS class for compiling attribute dictionary based on DB columns
    and mapping dict.
    """

    def __init__(self, mapping_dictionary, input_dictionary, db_columns, logger):
        self.mapping_dictionary = mapping_dictionary
        self.input_dictionary = input_dictionary
        self.db_columns = db_columns
        self.logger = logger

    def _transform(self, xml_tag):
        """
        Convert tags in XML to name in database (eg.StavDat to STAV_DAT)
        :param xml_tag: str - tag of xml attribute in xml response
        :rtype: str - column name in database
        """
        return re.sub("([A-Z]{1})", r"_\1", xml_tag).upper()

    def convert_attributes(self):
        """
        Draw up converted attribute dictionary based on mapping json file
        and transformed db column names.
        Raises:
            WSDPError
        :rtype: dict - output dictionary which matches tags in SQLITE db
        """
        output_dictionary = {}
        for posident_id, input_nested_dictionary in self.input_dictionary.items():
            output_nested_dictionary = {}
            # Go through nested dictionary keys and replace them
            for key in input_nested_dictionary.keys():
                if key in self.mapping_dictionary.keys():
                    new_key = self.mapping_dictionary[key]
                else:
                    new_key = self._transform(key)
                    if new_key not in self.db_columns:
                        raise WSDPError(
                            self.logger,
                            "XML attribute name cannot be converted to database column name",
                        )
                output_nested_dictionary[new_key] = input_nested_dictionary[key]
            output_dictionary[posident_id] = output_nested_dictionary
        return output_dictionary


class DbManager:
    """
    CtiOS class for managing VFK SQLite database created based on GDAL
    """

    def __init__(self, db_path, logger):
        """
        :param db_path: path to db file (str)
        :param logger: logger object (class Logger)
        """
        self.logger = logger
        self.db_path = db_path
        self.schema = "OPSUB"  # schema containning info about posidents
        self._check_db()
        self.conn = self._create_connection()

    def _check_db(self):
        """
        Control path to db
        Raises:
            WSDPError: FileNotFoundError
        """
        my_file = Path(self.db_path)
        try:
            # Control if database file exists
            my_file.resolve(strict=True)

        except FileNotFoundError as exc:
            raise WSDPError(self.logger, exc) from exc

    def _create_connection(self):
        """
        Create a database connection to the SQLite database specified by the db_path
        Raises:
            WSDPError: SQLite error
        """

        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as exc:
            raise WSDPError(self.logger, exc) from exc

    def get_posidents_from_db(self, sql=None):
        """
        Get posidents from db
        Raises:
            WSDPError: SQLite error (Raises when not possible to connect to db)
            WSDPError: Query has an empty result! (Raises when the response is empty)
        :param sql: optional SQL select statement for filtering (if not specified, all ids from db are selected)
        :rtype: dict - posident ids from db
        """
        if not sql:
            sql = "SELECT ID FROM OPSUB ORDER BY ID"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            ids = cur.fetchall()
        except sqlite3.Error as exc:
            raise WSDPError(self.logger, exc) from exc

        # Control if not empty
        if len(ids) <= 1:
            msg = "Query has an empty result!"
            raise WSDPError(self.logger, msg)

        posidents = []
        for i in list(set(ids)):
            posidents.append(i[0])

        return posidents

    def get_columns_names(self):
        """
        Get names of columns in schema
        Raises:
            WSDPError: SQLite error
        :rtype: list - column names in the given schema
        """
        try:
            cur = self.conn.cursor()
            cur.execute("PRAGMA read_committed = true;")
            cur.execute("""select * from {0}""".format(self.schema))
            return list(map(lambda x: x[0], cur.description))
        except sqlite3.Error as exc:
            raise WSDPError(self.logger, exc) from exc

    def add_column_to_db(self, name, datatype):
        """
        Add column to db
        Raises:
            WSDPError: SQLite error
        :param name: str - name of column
        :param datatype: str - column data type
        """
        col_names = self.get_columns_names()
        try:
            cur = self.conn.cursor()
            if name not in col_names:
                # Alter table by adding a new column
                cur.execute(
                    """ALTER TABLE {0} ADD COLUMN {1} {2}""".format(
                        self.schema, name, datatype
                    )
                )
        except sqlite3.Error as exc:
            raise WSDPError(self.logger, exc) from exc

    def update_rows_in_db(self, dictionary):
        """
        Save attribute dictionary to db
        Raises:
            WSDPError: SQLite error
        :param dictionary: nested dict - XML atributes mapped to DB space

        """
        try:
            cur = self.conn.cursor()
            cur.execute("BEGIN TRANSACTION")
            for posident_id, posident_info in dictionary.items():
                #  Update table OPSUB by database attributes items
                for dat_name in posident_info:
                    cur.execute(
                        """UPDATE {0} SET {1} = ? WHERE id = ?""".format(
                            self.schema, dat_name
                        ),
                        (posident_info[dat_name], posident_id),
                    )
                cur.execute("COMMIT TRANSACTION")
        except self.conn.Error as exc:
            cur.execute("ROLLBACK TRANSACTION")
            cur.close()
            raise WSDPError(self.logger, "Transaction failed!: {}".format(exc)) from exc

    def close_connection(self):
        if self.conn:
            self.conn.close()
