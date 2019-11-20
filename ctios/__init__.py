###############################################################################
# Name:         library CTI_OS
# Purpose:      Sends a request to CTI_OS service based on given posident array
#               and stores response to SQLITE DB
# Date:         May 2019
# Copyright:    (C) 2019 Linda Kladivova
# Email:        l.kladivova@seznam.cz
###############################################################################

import requests
import xml.etree.ElementTree as et
import sqlite3
import math
import logging
from datetime import datetime
import re
import os
from pathlib import Path

from ctios.exceptions import CtiOsError
import ctios.settings

from ctios.templates import CtiOsTemplate
from ctios.csv import CtiOsCsv


class CtiOs:

    def __init__(self, username, password, max_num=10):

        # CTI_OS authentication
        self._username = username
        self._password = password

        # CTI_OS service parameters
        self.endpoint = 'https://wsdptrial.cuzk.cz/trial/ws/ctios/2.8/ctios'
        self.headers = {'Content-Type': 'text/xml;charset=UTF-8',
                        'Accept-Encoding': 'gzip,deflate',
                        'SOAPAction': "http://katastr.cuzk.cz/ctios/ctios",
                        'Connection': 'Keep-Alive'}

        # Max number of ids inside one request
        self.max_num = max_num

    def set_db(self, db_path):
        """
        Setting of database
        :param db_path: path to db file
        :type db_path: string
        :returns response: Exception if ids in the database do not match ids in the text file
        """
        my_file = Path(db_path)
        try:
            # Control if database file exists
            my_file.resolve(strict=True)
            self.db_path = db_path

        except FileNotFoundError as e:
            raise CtiOsError(e)

    def set_posidents_from_db(self, sql=None):
        """
        Setting of input - posidents from db

        Raise CtiOsError when response ids is empty.

        :param str sql: SQL select statement for filtering or None
        """
        if sql is None:
            sql = "SELECT ID FROM OPSUB"
        self.ids = self._get_posidents_from_db(sql)

        # Control if not empty
        if len(self.ids) <= 1:
            raise CtiOsError("Query has an empty result!")

    def _get_posidents_from_db(self, sql):
        """
        Send query to database
        :param sql: sql query
        :type sql: string
        :returns response: CtiOsError if cannot find db
        """
        try:
            with self._create_connection() as conn:
                cur = conn.cursor()
                cur.execute(sql)
                ids = cur.fetchall()
                cur.close()
        except sqlite3.Error as e:
            raise CtiOsError("Database error!")

        return list(set(ids))

    def _draw_up_xml_request(self, ids):
        """
        Put together a request in the XML form to CTI_OS service
        :returns response: final XML request with all ids attributes
        :rtype response: list
        """

        posident_array = []

        for i in ids:

            # Trim id
            i = str(i)
            n = i[2:]
            m = n[:-3]

            # Draw up xml tag
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(m)

            # Add all tags to one list
            posident_array.append(row)

        # Convert list to one long string
        pos = ''.join(posident_array)

        # Render XML request
        self.xml = CtiOsTemplate(settings.TEMPLATES_DIR).render(
            'request.xml', username=self._username, password=self._password, posidents=pos
        )

    def _call_service(self):
        """
        Send a request in the XML form to CTI_OS service
        :raises: '3xx Redirect', '4xx Client Error', '5xx Server Error'
        :returns response: XML response with all ids attributes
        :rtype response: string
        """

        self.response = requests.post(self.endpoint, data=self.xml, headers=self.headers)
        self.status_code = self.response.status_code
        self.response = self.response.text

        # Errors
        if 300 <= self.status_code < 400:
            if self.log_path:
                self.logging.fatal('STAVOVY KOD HTTP 3xx: REDIRECT')
            raise CtiOsError("STAVOVY KOD HTTP 3xx: REDIRECT!")

        elif 400 <= self.status_code < 500:
            if self.log_path:
                self.logging.fatal('STAVOVY KOD HTTP 4xx: CLIENT ERROR!')
            raise CtiOsError("STAVOVY KOD HTTP 4xx: CLIENT ERROR!")

        elif 500 <= self.status_code < 600:
            if self.log_path:
                self.logging.fatal('STAVOVY KOD HTTP 5xx: SERVER ERROR!')
            raise CtiOsError("STAVOVY KOD HTTP 5xx: SERVER ERROR!")

        else:
            # Success
            if self.log_path:
                self.logging.info('STAVOVY KOD HTTP 2xx: SUCCESS!')
            return self.response

    def _create_connection(self):
        """
        Create a database connection to the SQLite database specified by the db_file
        :raises: 'SQLITE3 ERROR'
        :returns conn: Connection object
        :rtype conn: Connection object
        """
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Error:
            if self.log_path:
                self.logging.fatal('SQLITE3 ERROR!' + self.db_path)
            raise Exception("SQLITE3 ERROR" + self.db_path)

    @staticmethod
    def _transform_names(xml_name):
        """
        Convert names in XML name to name in database (eg. StavDat to stav_dat)
        :returns database_name: column names in database
        :rtype database_name: string
        """
        database_name = re.sub('([A-Z]{1})', r'_\1', xml_name).upper()
        return database_name

    def _transform_names_dict(self, xml_name):
        """
        Convert names in database to name in XML based on special dictionary
        :returns database_name: column names in database
        :rtype database_name: string
        """
        # key = name in XML
        # value = name in database
        try:
            database_name = self.dictionary[xml_name]
            return database_name
        except Exception:
            if self.log_path:
                self.logging.exception('XML ATTRIBUTE NAME CANNOT BE CONVERTED TO DATABASE COLUMN NAME')
            raise Exception("XML ATTRIBUTE NAME CANNOT BE CONVERTED TO DATABASE COLUMN NAME")

    def _save_attributes_to_db(self):
        """
        1. Parses XML returned by CTI_OS service into desired parts which will represent database table attributes
        2. Connects to Export_vse.db
        3. Alters table by adding OS_ID column if not exists
        4. Updates attributes for all posidents in SQLITE3 table rows
        Keyword arguments: xml file returned by CTI_OS service, path to the database file and state information vector, logging
        Returns: failed! if problem appears otherwise updated state vector
        """

        root = et.fromstring(self.response)

        for os in root.findall('.//{http://katastr.cuzk.cz/ctios/types/v2.8}os'):

            # Check errors of given ids, if error occurs continue back to the function beginning
            if os.find('{http://katastr.cuzk.cz/ctios/types/v2.8}chybaPOSIdent') is not None:
                posident = os.find('{http://katastr.cuzk.cz/ctios/types/v2.8}pOSIdent').text

                if os.find('{http://katastr.cuzk.cz/ctios/types/v2.8}chybaPOSIdent').text == "NEPLATNY_IDENTIFIKATOR":
                    self.state_vector['neplatny_identifikator'] += 1
                    if self.log_path:
                        self.logging.error('POSIDENT {} NEPLATNY IDENTIFIKATOR'.format(posident))
                    continue
                if os.find('{http://katastr.cuzk.cz/ctios/types/v2.8}chybaPOSIdent').text == "EXPIROVANY_IDENTIFIKATOR":
                    self.state_vector['expirovany_identifikator'] += 1
                    if self.log_path:
                        self.logging.error('POSIDENT {}: EXPIROVANY IDENTIFIKATOR'.format(posident))
                    continue
                if os.find(
                        '{http://katastr.cuzk.cz/ctios/types/v2.8}chybaPOSIdent').text == "OPRAVNENY_SUBJEKT_NEEXISTUJE":
                    self.state_vector['opravneny_subjekt_neexistuje'] += 1
                    if self.log_path:
                        self.logging.error('POSIDENT {}: OPRAVNENY SUBJEKT NEEXISTUJE'.format(posident))
                    continue
            else:
                self.state_vector['uspesne_stazeno'] += 1

            # Create the dictionary with XML child attribute names and particular texts
            for child in os:
                name = child.tag
                if name == '{http://katastr.cuzk.cz/ctios/types/v2.8}pOSIdent':
                    pos = os.find(name)
                    posident = pos.text
                if name == '{http://katastr.cuzk.cz/ctios/types/v2.8}osId':
                    o = os.find(name)
                    osid = o.text

            xml_attributes = {}
            for child in os.find('.//{http://katastr.cuzk.cz/ctios/types/v2.8}osDetail'):
                name2 = child.tag
                xml_attributes[child.tag[child.tag.index('}') + 1:]] = os.find('.//{}'.format(name2)).text

            # Find out the names of columns in database and if column os_id doesnt exist, add it
            try:
                conn = self._create_connection()
                cur = conn.cursor()
                cur.execute("PRAGMA read_committed = true;")
                cur.execute('select * from OPSUB')
                col_names = list(map(lambda x: x[0], cur.description))
                if 'OS_ID' not in col_names:
                    cur.execute('ALTER TABLE OPSUB ADD COLUMN OS_ID TEXT')
                cur.close()
            except conn.Error:
                cur.close()
                conn.close()
                if self.log_path:
                    self.logging.exception('Pripojeni k databazi selhalo')
                raise Exception("CONNECTION TO DATABASE FAILED")

            #  Transform xml_names to database_names
            database_attributes = {}
            self.dictionary = CtiOsCsv(settings.CSV_DIR).read_csv_as_dictionary(
                settings.ATTRIB_MAP_FILE
            )
            for xml_name, xml_value in xml_attributes.items():
                database_name = self._transform_names(xml_name)
                if database_name not in col_names:
                    database_name = self._transform_names_dict(xml_name)
                database_attributes.update({database_name: xml_value})

            #  Update table OPSUB by database_attributes items
            try:
                cur = conn.cursor()
                cur.execute("BEGIN TRANSACTION")
                for dat_name, dat_value in database_attributes.items():
                    cur.execute("""UPDATE OPSUB SET {0} = ? WHERE id = ?""".format(dat_name), (dat_value, posident))
                cur.execute("""UPDATE OPSUB SET OS_ID = ? WHERE id = ?""", (osid, posident))
                cur.execute("COMMIT TRANSACTION")
                cur.close()
                if self.log_path:
                    self.logging.info('Radky v databazi u POSIdentu {} aktualizovany'.format(posident))
            except conn.Error:
                print("failed!")
                cur.execute("ROLLBACK TRANSACTION")
                cur.close()
                conn.close()
            finally:
                if conn:
                    conn.close()
        if self.log_path:
            return self.state_vector

    def _query_service(self, ids):
        """
        Function which draws up xml request,
        call service and save attributes into db using other partial functions
        """
        self._draw_up_xml_request(ids)  # Putting XML request together
        self._call_service()  # CTI_OS request with upper parameters
        self._save_attributes_to_db()

    def query_requests(self):
        """
        Main function which divides requests into groups
        """

        if self.log_path:
            self.logging.info('Pocet jedinecnych ID v seznamu: {}'.format(len(self.ids)))

        if len(self.ids) <= self.max_num:
            ids = self.ids
            self._query_service(ids)  # Query and save response to db
            if self.log_path:
                self.logging.info('Zpracovano v ramci 1 pozadavku.')
        else:
            full_arrays = math.floor(len(self.ids) / self.max_num)  # Floor to number of full posidents arrays
            rest = len(self.ids) % self.max_num  # Left posidents
            for i in range(0, full_arrays):
                start = i * self.max_num
                end = i * self.max_num + self.max_num
                whole_ids = self.ids[start: end]
                self._query_service(whole_ids)  # Query and save response to db

            # make a request from the rest of posidents
            ids_rest = self.ids[len(self.ids) - rest: len(self.ids)]
            if ids_rest:
                self._query_service(ids_rest)  # Query and save response to db
                divided_into = full_arrays + 1
            else:
                divided_into = full_arrays

            if self.log_path:
                self.logging.info('Rozdeleno do {} pozadavku'.format(divided_into))

        if self.log_path:
            self.logging.info('Pocet uspesne stazenych posidentu: {} '.format(
                self.state_vector['uspesne_stazeno']))
            self.logging.info('Neplatny identifikator: {}x.'.format(
                self.state_vector['neplatny_identifikator']))
            self.logging.info('Expirovany identifikator: {}x.'.format(
                self.state_vector['expirovany_identifikator']))
            self.logging.info('Opravneny subjekt neexistuje: {}x.'.format(
                self.state_vector['opravneny_subjekt_neexistuje']))

    def set_log_file(self, log_path):
        """
        Create log file - not mandatory
        :param log_path: path to log file
        :type log_path: string
        :returns logging: Logging object
        :rtype conn: Logging object
        """

        logger = logging.getLogger('pyctios')
        self.log_path = log_path
        log_filename = datetime.now().strftime('%H_%M_%S_%d_%m_%Y.log')

        # set up logging to file - see previous section for more details
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=log_path + '/' + log_filename,
                            filemode='w')
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        # Create formatters and add it to handlers
        formatter = logging.Formatter('%(name)-12s - %(levelname)-8s - %(message)s')
        console.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(console)
        self.logging = logger

        # Initialization of state vector
        self.state_vector = {
            'neplatny_identifikator': 0,
            'expirovany_identifikator': 0,
            'opravneny_subjekt_neexistuje': 0,
            'uspesne_stazeno': 0}





