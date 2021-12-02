"""
@package ctiOS.helpers

@brief Base script for general classes needed for ctiOS service

Classes:
 - ctiOS::CtiOSXMLParser
 - ctiOS::CtiOSCounter
 - ctiOS::CtiOSDbManager
 - ctiOS::CtiOSXml2DbConverter


(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import re
import json
import sqlite3
from pathlib import Path
import xml.etree.ElementTree as et

from base.exceptions import WSDPError, WSDPResponseError


class CtiOSXMLParser:
    """Class parsing ctiOS XML response into a dictionary"""

    def __call__(self, content, counter, logger):
        """
        Read content from XML and parses it

        Args:
            content (str): content of XML response
            counter (class): counts posident errors
            logger (class): log class
        Returns:
            xml_attributes (nested dictonary): parsed XML attributes
        """
        root = et.fromstring(content)
        namespace = self._get_xml_namespace()
        namespace_length = len(namespace)
        xml_dict = {}

        # Find all tags with 'os' name
        for os_tag in root.findall(".//{}os".format(namespace)):

            # Save posident variable
            posident = os_tag.find("{}pOSIdent".format(namespace)).text

            if os_tag.find("{}chybaPOSIdent".format(namespace)) is not None:

                # Errors detected
                identifier = os_tag.find("{}chybaPOSIdent".format(namespace)).text

                if identifier == "NEPLATNY_IDENTIFIKATOR":
                    counter.add_neplatny_identifikator()
                elif identifier == "EXPIROVANY_IDENTIFIKATOR":
                    counter.add_expirovany_identifikator()
                elif identifier == "OPRAVNENY_SUBJEKT_NEEXISTUJE":
                    counter.add_opravneny_subjekt_neexistuje()

                # Write to log
                if identifier in (
                    "NEPLATNY_IDENTIFIKATOR",
                    "EXPIROVANY_IDENTIFIKATOR",
                    "OPRAVNENY_SUBJEKT_NEEXISTUJE",
                ):
                    logger.info(
                        "POSIDENT {} {}".format(posident, identifier.replace("_", " "))
                    )
                else:
                    raise WSDPResponseError(
                        logger,
                        "POSIDENT {} {}".format(posident, identifier.replace("_", " ")),
                    )
            else:
                # No errors detected
                xml_dict[posident] = {}
                counter.add_uspesne_stazeno()
                logger.info("POSIDENT {} USPESNE STAZEN".format(posident))

                # Create the dictionary with XML child attribute names and particular texts
                for child in os_tag.find(".//{}osDetail".format(namespace)):
                    # key: remove namespace from element name
                    name = child.tag
                    xml_dict[posident][name[namespace_length:]] = os_tag.find(
                        ".//{}".format(name)
                    ).text
                os_id = os_tag.find("{}osId".format(namespace)).text
                xml_dict[posident]["osId"] = os_id
        return xml_dict

    def _get_xml_namespace(self):
        return "{http://katastr.cuzk.cz/ctios/types/v2.8}"


class CtiOSCounter:
    """
    CtiOS class which counts posident stats
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


class CtiOSDbManager:
    """
    CtiOS class for managing VFK SQLite database created based on GDAL
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
            WSDPError: FileNotFoundError
        """
        my_file = Path(db_path)
        try:
            # Control if database file exists
            my_file.resolve(strict=True)
            return db_path

        except FileNotFoundError as e:
            raise WSDPError(self.logger, e)

    def _create_connection(self):
        """
        Create a database connection to the SQLite database specified by the db_path
        Raises:
            WSDPError: SQLite error
        """

        try:
            self.conn = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise WSDPError(self.logger, e)

    def get_posidents_from_db(self, sql=None):
        """
        Get posidents from db
        Args:
            sql (str): SQL select statement for filtering or None (if not specified, all ids from db are selected)
        Raises:
            WSDPError: SQLite error (Raises when not possible to connect to db)
            WSDPError: Query has an empty result! (Raises when the response is empty)
        Returns:
            ids_dict (dict): pseudo ids from db
        """
        if not sql:
            sql = "SELECT ID FROM OPSUB ORDER BY ID"
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            self.conn.commit()
            ids = cur.fetchall()
        except sqlite3.Error as e:
            raise WSDPError(self.logger, e)

        # Control if not empty
        if len(ids) <= 1:
            msg = "Query has an empty result!"
            raise WSDPError(self.logger, msg)

        posidents = []
        for i in list(set(ids)):
            posidents.append(i[0])

        return posidents

    def get_columns_names(self, schema):
        """
        Get names of columns in schema
        Args:
            schema (str): name of schema in db
        Raises:
            WSDPError: SQLite error
         Returns:
             col_names (list): column names in given schema
        """
        try:
            cur = self.conn.cursor()
            cur.execute("PRAGMA read_committed = true;")
            cur.execute("""select * from {0}""".format(schema))
            col_names = list(map(lambda x: x[0], cur.description))
        except sqlite3.Error as e:
            raise WSDPError(self.logger, e)
        return col_names

    def add_column_to_db(self, schema, name, datatype):
        """
        Add column to db
        Args:
            schema (str): name of schema in db
            name (str): name of column
            datatype (str): column data type
        Raises:
            WSDPError: SQLite error
        """
        col_names = self.get_columns_names(schema)
        try:
            cur = self.conn.cursor()
            if name not in col_names:
                cur.execute(
                    """ALTER TABLE {0} ADD COLUMN {1} {2}""".format(
                        schema, name, datatype
                    )
                )
        except sqlite3.Error as e:
            raise WSDPError(self.logger, e)

    def save_attributes_to_db(self, schema, dictionary):
        """
        Save dictionary attributes to db
        Args:
            schema (str): name of schema in db
            dictionary (nested dictonary): converted DB attributes
            counter (class): class managing statistics info
        Raises:
            WSDPError: SQLite error
        """
        try:
            cur = self.conn.cursor()
            cur.execute("BEGIN TRANSACTION")
            for posident_id, posident_info in dictionary.items():
                #  Update table OPSUB by database attributes items
                for dat_name in posident_info:
                    cur.execute(
                        """UPDATE OPSUB SET {0} = ? WHERE id = ?""".format(dat_name),
                        (posident_info[dat_name], posident_id),
                    )
                cur.execute("COMMIT TRANSACTION")
        except self.conn.Error as e:
            cur.execute("ROLLBACK TRANSACTION")
            cur.close()
            raise WSDPError(self.logger, "Transaction failed!: {}".format(e))

    def close_connection(self):
        if self.conn:
            self.conn.close()


class CtiOSXml2DbConverter:
    """
    CtiOS class for converting XML attribute names to DB attribute names
    """
    def __init__(self, mapping_attributes_path, logger):
        self.logger = logger
        self.mapping_attributes_path = mapping_attributes_path

    def _read_mapping_attributes_dir(self):
        """
        Read csv attributes as dictionary

        Args:
            csv_name (str): name of attribute mapping csv file

        Returns:
            dictionary (dict): (1.column:2.column)
        """
        with open(self.mapping_attributes_path) as json_file:
            return json.load(json_file)
        return None

    def _transform_names(self, xml_name):
        """
        Convert names in XML name to name in database (eg. StavDat to STAV_DAT)

        Args:
            xml_name (str): tag of xml attribute in xml response

        Returns:
            database_name (str): column names in database
        """

        database_name = re.sub("([A-Z]{1})", r"_\1", xml_name).upper()
        return database_name

    def _transform_names_dict(self, xml_name):
        """
        Convert names in XML name to name in database based on special dictionary

        Args:
            xml_name (str): tag of xml attribute in xml response
            config_file (str): configuration file (not mandatory)

        Raises:
            WSDPError(XML ATTRIBUTE NAME CANNOT BE CONVERTED TO DATABASE COLUMN NAME)

        Returns:
            database_name (str): column names in database
        """
        try:
            # Load dictionary with names of XML tags and their relevant database names
            mapping_attributes_dict = self._read_mapping_attributes_dir()
            database_name = mapping_attributes_dict[xml_name]
            return database_name

        except Exception as e:
            raise WSDPError(
                self.logger,
                "XML ATTRIBUTE NAME CANNOT BE CONVERTED TO DATABASE COLUMN NAME: {}".format(
                    e
                ),
            )

    def convert_attributes(self, db_columns, input_dictionary):
        """
        Convert XML attribute names to db attributes names

        Args:
            columns: list of columns in db
            input dictionary (nested dictonary): original XML attributes

        Returns:
            output dictionary (nested dictonary): converted DB attributes
        """
        output_dictionary = {}

        for posident_id, input_nested_dictionary in input_dictionary.items():
            output_nested_dictionary = {}
            for xml_key, value in input_nested_dictionary.items():
                db_key = self._transform_names(xml_key)
                if db_key not in db_columns:
                    db_key = self._transform_names_dict(xml_key)
                output_nested_dictionary[db_key] = value
            output_dictionary[posident_id] = output_nested_dictionary
        return output_dictionary