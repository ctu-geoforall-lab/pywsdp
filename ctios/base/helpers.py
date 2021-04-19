"""
@package ctios.base

@brief Base script for general classes needed for CtiOs service

Classes:
 - base::CtiOsDbManager
 - base::CtiOsXMLParser
 - base::CtiOsConverter
 - base::CtiOsCounter


(C) 2021 Linda Kladivova l.kladivova@seznam.cz
This library is free under the GNU General Public License.
"""

import re
import os
import csv
import sqlite3
import configparser
import xml.etree.ElementTree as et
from pathlib import Path

from base.exceptions import CtiOsError, CtiOsResponseError, CtiOsDbError, CtiOsInfo


class CtiOsDbManager:
    """
    CTIOS class for managing VFK SQLite database
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
            raise CtiOsDbError(e)

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
            raise CtiOsDbError(e)
        
        # Control if not empty
        if len(ids) <= 1:
            msg = "Query has an empty result!"
            raise CtiOsDbError(msg)
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
            raise CtiOsDbError(e)
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
            raise CtiOsDbError(e)

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
            raise CtiOsDbError("Transaction Failed!: {}".format(e))
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


class CtiOsXMLParser():

    def __call__(self, xml_content, counter, logger=None):
        """
        Read content from XML and parses it

        Args:
            xml_content (str): content of XML response
            namespace (str): XML CtiOs namespace
            counter (class): counts posident errors

        Returns:
            xml_attributes (nested dictonary): parsed XML attributes
        """
        root = et.fromstring(xml_content)
        namespace = self._get_xml_namespace(xml_content)
        namespace_length = len(namespace)
        xml_dict = {}

        # Find all tags with 'os' name
        for os_tag in root.findall('.//{}os'.format(namespace)):

            xml_dict[os_tag] = {}

            # Save posident variable
            posident = os_tag.find('{}pOSIdent'.format(namespace)).text

            if os_tag.find('{}chybaPOSIdent'.format(namespace)) is not None:

                # Errors detected
                identifier = os_tag.find('{}chybaPOSIdent'.format(namespace)).text

                if identifier == "NEPLATNY_IDENTIFIKATOR":
                    counter.add_neplatny_identifikator()
                elif identifier == "EXPIROVANY_IDENTIFIKATOR":
                    counter.add_expirovany_identifikator()
                elif identifier == "OPRAVNENY_SUBJEKT_NEEXISTUJE":
                    counter.add_opravneny_subjekt_neexistuje()
                else:
                    raise CtiOsResponseError('Unknown chybaPOSIdent')
                if logger:
                    logger.error('POSIDENT {} {}'.format(posident, identifier.replace('_', ' ')))
            else:
                # No errors detected
                # Create the dictionary with XML child attribute names and particular texts
                for child in os_tag.find('.//{}osDetail'.format(namespace)):
                    # key: remove namespace from element name
                    name = child.tag
                    xml_dict[os][name[namespace_length:]] = os_tag.find('.//{}'.format(name)).text
        return xml_dict

    def _get_xml_namespace(self):
        return '{http://katastr.cuzk.cz/ctios/types/v2.8}'


class CtiOsConverter():
    """
    CTIOS class for converting XML attribute names to DB attribute names
    """
    def __init__(self, input_dictionary):
        self.input_dictonary = input_dictionary

    def _get_mapping_attributes_dir(self, csv_dir):
        """
        Args:
          csv_dir (str): Csv directory has to be absolute path, relative paths are not supported
        """
        if csv_dir and os.path.isabs(csv_dir):
            self.csv_dir = csv_dir
        else:
            # relative paths are not supported
            self.csv_dir = os.path.join(
                os.path.dirname(__file__)
            )

    def _read_mapping_attributes_dir(self, csv_name):
        """
        Read csv attributes as dictionary

        Args:
            csv_name (str): name of attribute mapping csv file

        Returns:
            dictionary (dict): (1.column:2.column)
        """
        dictionary = {}
        with open(os.path.join(self.mapping_attributes_dir, csv_name)) as csv_file:
            rows = csv.reader(csv_file, delimiter=';')
            for row in rows:
                [k, v, l] = row
                dictionary[k] = v
            return dictionary

    def _transform_names(xml_name):
        """
        Convert names in XML name to name in database (eg. StavDat to STAV_DAT)

        Args:
            xml_name (str): tag of xml attribute in xml response

        Returns:
            database_name (str): column names in database
        """

        database_name = re.sub('([A-Z]{1})', r'_\1', xml_name).upper()
        return database_name

    def _transform_names_dict(self, xml_name, config_file=None):
        """
        Convert names in XML name to name in database based on special dictionary

        Args:
            xml_name (str): tag of xml attribute in xml response
            config_file (str): configuration file (not mandatory)

        Raises:
            CtiOsError(XML ATTRIBUTE NAME CANNOT BE CONVERTED TO DATABASE COLUMN NAME)

        Returns:
            database_name (str): column names in database
        """
        try:
            # Read configuration
            self._config = configparser.ConfigParser()
            if config_file is None:
                config_file = os.path.join(os.path.abspath('ctios'), 'settings.ini')
            self._config.read(config_file)

            # Load dictionary with names of XML tags and their relevant database names
            self.mapping_attributes_dir = self._get_mapping_attributes_dir(self._config['files'].get('csv_dir'))
            mapping_attributes_dict = self._read_mapping_attributes_dir(self._config['files']['attribute_map_file'])
            database_name = mapping_attributes_dict[xml_name]
            return database_name

        except Exception as e:
            raise CtiOsError("XML ATTRIBUTE NAME CANNOT BE CONVERTED TO DATABASE COLUMN NAME: {}".format(e))

    def convert_attributes(self, db_columns):
        """
        Convert XML attribute names to db attributes names

        Args:
            dictionary (nested dictonary): original XML attributes

        Returns:
            dictionary (nested dictonary): converted DB attributes
        """
        for posident_id, posident_info in self.input_dictonary.items():
            #  Convert attributes
            for dat_name in posident_info:
                dat_name = self._transform_names(dat_name)
                if dat_name not in db_columns:
                    dat_name = self._transform_names_dict(dat_name)


class CtiOsCounter():
    """
    CTIOS class which counts posident stats
    """

    def __init__(self):
        self.neplatny_identifikator = 0
        self.expirovany_identifikator = 0
        self.opravneny_subjekt_neexistuje = 0
        self.uspesne_stazeno = 0

    def add_neplatny_identifikator(self):
        self.neplatny_identifikator += 1

    def add_expirovany_identifikator(self):
        self.expirovany_identifikator += 1

    def add_opravneny_subjekt_neexistuje(self):
        self.opravneny_subjekt_neexistuje += 1

    def add_uspesne_stazeno(self):
        self.uspesne_stazeno += 1