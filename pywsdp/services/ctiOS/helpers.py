"""
@package ctiOS.helpers

@brief Base script for general classes needed for ctiOS service

Classes:
 - ctiOS::CtiOSXMLParser
 - ctiOS::CtiOSCounter
 - ctiOS::CtiOSDbManager
 - ctiOS::CtiOsAttributeConverter


(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import re
import json
import sqlite3
from pathlib import Path
import xml.etree.ElementTree as et

from pywsdp.base.exceptions import WSDPError, WSDPResponseError


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
        def get_xml_namespace_ns0():
            return "{http://katastr.cuzk.cz/ctios/types/v2.8}"

        def get_xml_namespace_ns1():
            return "{http://katastr.cuzk.cz/commonTypes/v2.8}"

        root = et.fromstring(content)

        # Find tags with 'zprava' name
        xml_dict = {}
        namespace_ns1 = get_xml_namespace_ns1()
        os_tags = root.findall(".//{}zprava".format(namespace_ns1))
        for os_tag in os_tags:
            logger.info(os_tag.text)

        # Find all tags with 'os' name
        namespace_ns0 = get_xml_namespace_ns0()
        namespace_length = len(namespace_ns0)
        for os_tag in root.findall(".//{}os".format(namespace_ns0)):

            # Save posident variable
            posident = os_tag.find("{}pOSIdent".format(namespace_ns0)).text

            if os_tag.find("{}chybaPOSIdent".format(namespace_ns0)) is not None:

                # Errors detected
                identifier = os_tag.find("{}chybaPOSIdent".format(namespace_ns0)).text

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
                for child in os_tag.find(".//{}osDetail".format(namespace_ns0)):
                    # key: remove namespace from element name
                    name = child.tag
                    xml_dict[posident][name[namespace_length:]] = os_tag.find(
                        ".//{}".format(name)
                    ).text
                os_id = os_tag.find("{}osId".format(namespace_ns0)).text
                xml_dict[posident]["osId"] = os_id
        return xml_dict


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


class CtiOSAttributeConverter:
    """
    CtiOS class for compiling attribute dictionary based on DB columns
    and mapping json file.
    """
    def __init__(self, mapping_attributes_path, input_dictionary, db_columns,  logger):
        self.mapping_attributes_path = mapping_attributes_path
        self.input_dictionary = input_dictionary
        self.db_columns = db_columns
        self.logger = logger

    def _read_mapping_attributes_dict(self):
        """
        Read json attributes as dictionary.
        The dictionary consists of db columns (keys) and xml tags (values).

        Args:
            csv_name (str): name of attribute mapping csv file

        Returns:
            dictionary (dict): (db_column: xml_tag)
        """
        with open(self.mapping_attributes_path) as json_file:
            return json.load(json_file)
        return None

    def _transform(self, xml_tag):
        """
        Convert tags in XML to name in database (eg.StavDat to STAV_DAT)

        Args:
            xml_tag (str): tag of xml attribute in xml response

        Returns:
            database_name (str): column names in database 
        """
        return re.sub("([A-Z]{1})", r"_\1", xml_tag).upper()

    def convert_attributes(self):
        """
        Draw up converted attribute dictionary based on mapping json file
        and transformed db column names.

        Returns:
            output dictionary (nested dictonary): converted XML tags
        """
        output_dictionary = {}
        mapping_dictionary = self._read_mapping_attributes_dict()
        for posident_id, input_nested_dictionary in self.input_dictionary.items():
            output_nested_dictionary = {}
            # Go through nested dictionary keys and replace them
            for key in input_nested_dictionary.keys():
                if key in mapping_dictionary.keys():
                    new_key = mapping_dictionary[key]
                else:
                    new_key = self._transform(key)
                    if new_key not in self.db_columns:
                        raise WSDPError(
                                self.logger,
                                "XML attribute name cannot be converted to database column name"
                        )
                output_nested_dictionary[new_key] = input_nested_dictionary[key]
            output_dictionary[posident_id] = output_nested_dictionary
        return output_dictionary
