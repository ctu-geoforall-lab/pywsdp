import os
import re
import csv
import math
import logging
import json
import sqlite3
from enum import Enum
from pathlib import Path
import xml.etree.ElementTree as et
from abc import ABC, abstractmethod
from datetime import datetime
from lxml import etree
import shutil


from zeep import Client, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
from zeep.plugins import HistoryPlugin


class OutputFormat(Enum):
    GdalDb = 1
    Json = 2
    Csv = 3


XML2DB_mapping = {
    "priznakKontext": "PRIZNAK_KONTEXTU",
    "partnerBsm1": "ID_JE_1_PARTNER_BSM",
    "partnerBsm2": "ID_JE_2_PARTNER_BSM",
    "charOsType": "CHAROS_KOD",
    "kodAdresnihoMista": "KOD_ADRM",
    "idNadrizenePravnickeOsoby": "ID_NADRIZENE_PO",
}


class WSDPLogger(logging.getLoggerClass()):
    """
    General WSDP class for logging
    """

    def __init__(self, name: str, level=logging.DEBUG):
        """
        Contructor of WSDPLogger class, format console handler
        :param name: service name (str)
        :param level: logging level ()
        """
        super().__init__(name)

        # Define a level of log messages
        logging.basicConfig(level=level)

        # Define a Stream Console Handler
        console = logging.StreamHandler()

        # Create formats and add it to console handler
        formatter = logging.Formatter("%(name)-12s - %(levelname)-8s - %(message)s")
        console.setFormatter(formatter)

        # Add handlers to the logger
        self.addHandler(console)

    def set_directory(self, log_dir: dir):
        """
        Set log directory
        :param log_dir: path to log directory (str)
        """

        log_filename = datetime.now().strftime("%H_%M_%S_%d_%m_%Y.log")

        self.file_handler = logging.FileHandler(
            filename=log_dir + "/" + log_filename, mode="w"
        )

        formatter = logging.Formatter("%(name)-12s %(asctime)s %(levelname)-8s %(message)s")
        self.file_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.addHandler(self.file_handler)

    def __del__(self):
        logging.shutdown()


xmlNamespace0 = {
    "sestavy": "{http://katastr.cuzk.cz/sestavy/types/v2.9}",
    "ctios": "{http://katastr.cuzk.cz/ctios/types/v2.8}",
}

xmlNamespace1 = {
    "sestavy": "{http://katastr.cuzk.cz/commonTypes/v2.9}",
    "ctios": "{http://katastr.cuzk.cz/commonTypes/v2.8}",
}

trialWsdls = {
    "sestavy": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/sestavy_v29.wsdl",
    "ciselnik": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/ciselnik_v29.wsdl",
    "vyhledat": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/vyhledat_v29.wsdl",
    "informace": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/informace_v29.wsdl",
    "ucet": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/ucet_v29.wsdl",
    "ctios": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws28/ctios/ctios_v28.wsdl",
}

prodWsdls = {
    "sestavy": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/sestavy_v29.wsdl",
    "ciselnik": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/ciselnik_v29.wsdl",
    "vyhledat": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/vyhledat_v29.wsdl",
    "informace": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/informace_v29.wsdl",
    "ucet": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/ucet_v29.wsdl",
    "ctios": "https://katastr.cuzk.cz/dokumentace/ws28/ctios/ctios_v28.wsdl",
}

transport = Transport(cache=SqliteCache())
settings = Settings(raw_response=False, strict=False, xml_huge_tree=True)
settings = Settings(strict=False, xml_huge_tree=True)
history = HistoryPlugin()


class WSDPClient(ABC):
    @classmethod
    def from_recipe(cls, wsdl, service_name, creds, logger, trial):
        """
        Method used by factory for creating instances of WSDP client classes.
        :param wsdl: link to wsdl document (str)
        :param service_name: name of the service used in CUZK documentation (str)
        :param creds: credentials to WSDP (dict)
        :rtype: Cient class
        """
        result = cls()
        if trial is True:
            result.client = Client(
                trialWsdls[wsdl],
                transport=transport,
                wsse=UsernameToken(*creds),
                settings=settings,
                plugins=[history],
            )
        else:
            result.client = Client(
                prodWsdls[wsdl],
                transport=transport,
                wsse=UsernameToken(*creds),
                settings=settings,
                plugins=[history],
            )
        result.service_name = service_name
        result.logger = logger
        result.creds = creds
        return result

    @abstractmethod
    def send_request(self, *args):
        """
        Method for sending a request to a service. Must be defined by all child classes.
        """

    def zeep_object_to_xml(self):
        """
        Convert output zeep object to XML object using lxml library.
        """
        try:
            for hist in [history.last_sent, history.last_received]:
                response_xml = etree.tostring(
                    hist["envelope"], encoding="unicode", pretty_print=True
                )
            return response_xml
        except (IndexError, TypeError) as e:
            raise WSDPRequestError(self.logger, e) from e


class SestavyClient(WSDPClient):

    service_group = "sestavy"

    def zeep_object_to_dict(self):
        """
        Convert output zeep object to dict object using lxml library and own parsering class.
        """
        response_xml = self.zeep_object_to_xml()
        return SestavyXMLParser()(content=response_xml, logger=self.logger)


class WSDPFactory:
    def __init__(self):
        self.classes = {}

    def register(self, cls):
        self.classes[cls.service_name] = cls
        return cls

    def create(self, *args):
        if args[1]:
            service_name = args[1]
        cls = self.classes[service_name]
        return cls.from_recipe(*args)


pywsdp = WSDPFactory()


class WSDPError(Exception):
    """Another exception for errors caused by reading, parsing XML"""

    def __init__(self, logger, msg):
        logger.fatal(msg)


class WSDPRequestError(WSDPError):
    """Basic exception for errors raised by requesting any WSDP service"""

    def __init__(self, logger, msg):
        super().__init__(logger, "{} - {}".format("WSDP REQUEST ERROR", msg))


class WSDPResponseError(WSDPError):
    """Basic exception for errors raised by responses from any WSDP service"""

    def __init__(self, logger, msg):
        super().__init__(logger, "{} - {}".format("WSDP RESPONSE ERROR", msg))


class CtiOSXMLParser:
    """Class parsing ctiOS XML response into a dictionary."""

    def __call__(self, content, counter, logger):
        """
        Read content from XML and parses it.
        Raised:
            WSDPResponseError
        :param content: XML response (str)
        :param counter: counts posident errors (CtiOSCounter class)
        :param logger: logging class (Logger)
        :rtype: parsed XML attributes (nested dictonary)
        """
        root = et.fromstring(content)

        # Find tags with 'zprava' name
        xml_dict = {}
        namespace_ns1 = xmlNamespace1["ctios"]
        os_tags = root.findall(".//{}zprava".format(namespace_ns1))
        for os_tag in os_tags:
            logger.info(" ")
            logger.info(os_tag.text)

        # Find all tags with 'os' name
        namespace_ns0 = xmlNamespace0["ctios"]
        namespace_length = len(namespace_ns0)
        for os_tag in root.findall(".//{}os".format(namespace_ns0)):

            # Save posident variable
            posident = os_tag.find("{}pOSIdent".format(namespace_ns0)).text

            if os_tag.find("{}chybaPOSIdent".format(namespace_ns0)) is not None:

                # Detect errors
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


class SestavyXMLParser:
    """Class parsing sestavy XML response into a dictionary"""

    def __call__(self, content, logger):
        """
        Read content from XML and parses it.
        Raises:
            WSDPResponseError
        :param content: XML response (str)
        :param logger: logging class (Logger)
        :rtype: parsed XML attributes (nested dictonary)
        """
        root = et.fromstring(content)

        # Find tags with 'zprava' name
        xml_dict = {}
        namespace_ns1 = xmlNamespace1["sestavy"]
        os_tags = root.findall(".//{}zprava".format(namespace_ns1))
        for os_tag in os_tags:
            xml_dict["zprava"] = os_tag.text
            logger.info(" ")
            logger.info(os_tag.text)

        # Find all tags with 'report' name
        namespace_ns0 = xmlNamespace0["sestavy"]
        for os_tag in root.findall(".//{}report".format(namespace_ns0)):

            # Id sestavy
            xml_dict["idSestavy"] = os_tag.find("{}id".format(namespace_ns0)).text
            if xml_dict["idSestavy"]:
                logger.info("ID sestavy: {}".format(xml_dict["idSestavy"]))
            else:
                raise WSDPResponseError(logger, "ID sestavy nebylo vraceno")

            # Nazev sestavy
            if os_tag.find("{}nazev".format(namespace_ns0)) is not None:
                xml_dict["nazev"] = os_tag.find("{}nazev".format(namespace_ns0)).text
                logger.info("Nazev sestavy: {}".format(xml_dict["nazev"]))

            # Pocet jednotek
            if os_tag.find("{}pocetJednotek".format(namespace_ns0)) is not None:
                xml_dict["pocetJednotek"] = os_tag.find(
                    "{}pocetJednotek".format(namespace_ns0)
                ).text
                logger.info("Pocet jednotek: {}".format(xml_dict["pocetJednotek"]))

            # Pocet stran
            if os_tag.find("{}pocetStran".format(namespace_ns0)) is not None:
                xml_dict["pocetStran"] = os_tag.find(
                    "{}pocetStran".format(namespace_ns0)
                ).text
                logger.info("Pocet stran: {}".format(xml_dict["pocetStran"]))

            # Cena
            if os_tag.find("{}cena".format(namespace_ns0)) is not None:
                xml_dict["cena"] = os_tag.find("{}cena".format(namespace_ns0)).text
                logger.info("Cena: {}".format(xml_dict["cena"]))

            # Datum pozadavku
            if os_tag.find("{}datumPozadavku".format(namespace_ns0)) is not None:
                xml_dict["datumPozadavku"] = os_tag.find(
                    "{}datumPozadavku".format(namespace_ns0)
                ).text
                logger.info("Datum pozadavku: {}".format(xml_dict["datumPozadavku"]))

            # Datum spusteni
            if os_tag.find("{}datumSpusteni".format(namespace_ns0)) is not None:
                xml_dict["datumSpusteni"] = os_tag.find(
                    "{}datumSpusteni".format(namespace_ns0)
                ).text
                logger.info("Datum spusteni: {}".format(xml_dict["datumSpusteni"]))

            # Datum vytvoreni
            if os_tag.find("{}datumVytvoreni".format(namespace_ns0)) is not None:
                xml_dict["datumVytvoreni"] = os_tag.find(
                    "{}datumVytvoreni".format(namespace_ns0)
                ).text
                logger.info("Datum vytvoreni: {}".format(xml_dict["datumVytvoreni"]))

            # Stav sestavy
            if os_tag.find("{}stav".format(namespace_ns0)) is not None:
                xml_dict["stav"] = os_tag.find("{}stav".format(namespace_ns0)).text
                logger.info("Stav sestavy: {}".format(xml_dict["stav"]))

            # Format
            if os_tag.find("{}format".format(namespace_ns0)) is not None:
                xml_dict["format"] = os_tag.find("{}format".format(namespace_ns0)).text
                logger.info("Format sestavy: {}".format(xml_dict["format"]))

            # Elektronicka znacka
            if os_tag.find("{}elZnacka".format(namespace_ns0)) is not None:
                xml_dict["elZnacka"] = os_tag.find(
                    "{}elZnacka".format(namespace_ns0)
                ).text
                logger.info("Elektronicka znacka: {}".format(xml_dict["elZnacka"]))

            # Soubor sestavy
            if os_tag.find("{}souborSestavy".format(namespace_ns0)) is not None:
                xml_dict["souborSestavy"] = os_tag.find(
                    "{}souborSestavy".format(namespace_ns0)
                ).text

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


class CtiOSAttributeConverter:
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


class CtiOSDbManager:
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

        except FileNotFoundError as e:
            raise WSDPError(self.logger, e) from e

    def _create_connection(self):
        """
        Create a database connection to the SQLite database specified by the db_path
        Raises:
            WSDPError: SQLite error
        """

        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise WSDPError(self.logger, e) from e

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
        except sqlite3.Error as e:
            raise WSDPError(self.logger, e) from e

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
        except sqlite3.Error as e:
            raise WSDPError(self.logger, e) from e

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
        except sqlite3.Error as e:
            raise WSDPError(self.logger, e) from e

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
        except self.conn.Error as e:
            cur.execute("ROLLBACK TRANSACTION")
            cur.close()
            raise WSDPError(self.logger, "Transaction failed!: {}".format(e)) from e

    def close_connection(self):
        if self.conn:
            self.conn.close()


@pywsdp.register
class CtiOsClient(WSDPClient):
    """
    Client for communicating with CtiOS WSDP service.
    """

    service_name = "ctiOS"
    service_group = "ctios"

    def __init__(self):
        super().__init__()
        self.posidents_per_request = 10  # Set max number of posidents per request
        self.number_of_posidents = 0
        self.number_of_posidents_final = 0
        self.response_xml = []
        self.parser = CtiOSXMLParser()
        self.counter = CtiOSCounter() # Counts statistics
        
        
    def send_request(self, dictionary):
        """
        Send the request in the form of dictionary and get the response.
        Raises:
            WSDPRequestError: Zeep library request error
        :param dictionary: input service attributes
        :rtype: list - xml responses divided based on chunks
        """

        def create_chunks(lst, n):
            """ "Create n-sized chunks from list as a generator"""
            n = max(1, n)
            return (lst[i : i + n] for i in range(0, len(lst), n))

        # Save statistics
        self.number_of_posidents = len(dictionary["pOSIdent"])

        # Remove duplicates
        posidents = list(dict.fromkeys(dictionary["pOSIdent"]))
        self.number_of_posidents_final = len(posidents)

        # create chunks
        chunks = create_chunks(posidents, self.posidents_per_request)

        # process posident chunks and return xml response as the dict
        response_dict = {}
        for chunk in chunks:
            try:
                self.client.service.ctios(pOSIdent=chunk)
                item = self.zeep_object_to_xml()
            except Exception as e:
                raise WSDPRequestError(self.logger, e) from e

            # save to raw xml list
            self.response_xml.append(item)

            # create response dictionary
            partial_dictionary = self.parser(
                content=item, counter=self.counter, logger=self.logger
            )
            response_dict = {**response_dict, **partial_dictionary}
        return response_dict

    def print_statistics(self):
        """
        Print statistics of the process to the standard output device.
        """
        print(
            {
                "celkovy pocet identifikatoru na vstupu": self.number_of_posidents,
                "pocet odstranenych duplicit": self.number_of_posidents
                - self.number_of_posidents_final,
                "pocet dotazu na server": math.ceil(
                    self.number_of_posidents_final
                    / self.posidents_per_request
                ),
                "pocet uspesne zpracovanych identifikatoru": self.counter.uspesne_stazeno,
                "pocet neplatnych identifikatoru": self.counter.neplatny_identifikator,
                "pocet expirovanych identifikatoru": self.counter.expirovany_identifikator,
                "pocet identifikatoru k neexistujicim OS": self.counter.opravneny_subjekt_neexistuje,
            }
        )

    def log_statistics(self):
        """Log statistics of the process to the log file."""
        self.logger.info(
            "Celkovy pocet dotazovanych identifikatoru na vstupu: {}".format(
                self.number_of_posidents
            )
        )
        self.logger.info(
            "Pocet odstranenych duplicitnich identifikatoru: {}".format(
                self.number_of_posidents - self.number_of_posidents_final
            )
        )
        self.logger.info(
            "Pocet pozadavku, do kterych byl dotaz rozdelen (pocet dotazu na server): {}".format(
                math.ceil(
                    self.number_of_posidents_final
                    / self.posidents_per_request
                )
            )
        )
        self.logger.info(
            "Realny uspesne zpracovanych identifikatoru: {}".format(
                self.counter.uspesne_stazeno
            )
        )
        self.logger.info(
            "Pocet neplatnych identifikatoru: {}".format(
                self.counter.neplatny_identifikator
            )
        )
        self.logger.info(
            "Pocet expirovanych identifikatoru: {}".format(
                self.counter.expirovany_identifikator
            )
        )
        self.logger.info(
            "Pocet identifikatoru k neexistujicim OS: {}".format(
                self.counter.opravneny_subjekt_neexistuje
            )
        )

@pywsdp.register
class GenerujCenoveUdajeDleKuClient(SestavyClient):
    """
    Client for communicating with GenerujCenoveUdajeDleKu WSDP service.
    """

    service_name = "generujCenoveUdajeDleKu"
    service_group = "sestavy"

    def send_request(self, dictionary):
        """
        Send the request with input dictionary and get the response.
        Raises:
            WSDPRequestError: Zeep library request error
        :param dictionary: dictionary of input attributes
        :rtype: str - xml responses
        """
        try:
            self.client.service.generujCenoveUdajeDleKu(
                katastrUzemiKod=dictionary["katastrUzemiKod"],
                rok=dictionary["rok"],
                mesicOd=dictionary["mesicOd"],
                mesicDo=dictionary["mesicDo"],
                format=dictionary["format"],
            )
            return self.zeep_object_to_dict()
        except Exception as e:
            raise WSDPRequestError(self.logger, e) from e


@pywsdp.register
class SeznamSestavClient(SestavyClient):
    """
    Client for communicating with SeznamSestav WSDP service.
    """

    service_name = "seznamSestav"
    service_group = "sestavy"

    def send_request(self, id_sestavy):
        """
        Send the request on specific id and get the response.
        Raises:
            WSDPRequestError: Zeep library request error
        :param id_sestavy: id (number)
        :rtype: list - xml responses
        """
        try:
            self.client.service.seznamSestav(idSestavy=id_sestavy)
            return self.zeep_object_to_dict()
        except Exception as e:
            raise WSDPRequestError(self.logger, e) from e


@pywsdp.register
class VratSestavuClient(SestavyClient):
    """
    Client for communicating with VratSestavu WSDP service.
    """

    service_name = "vratSestavu"
    service_group = "sestavy"

    def send_request(self, id_sestavy):
        """
        Send the request on specific id and get the response.
        Raises:
            WSDPRequestError: Zeep library request error
        :param id_sestavy: id (number)
        :rtype: list - xml responses
        """
        try:
            self.client.service.vratSestavu(idSestavy=id_sestavy)
            return self.zeep_object_to_dict()
        except Exception as e:
            raise WSDPRequestError(self.logger, e)


@pywsdp.register
class SmazSestavuClient(SestavyClient):
    """
    Client for communicating with SmazSestavu WSDP service.
    """

    service_name = "smazSestavu"
    service_group = "sestavy"

    def send_request(self, id_sestavy):
        """
        Send the request on specific id and get the response.
        Raises:
            WSDPRequestError: Zeep library request error
        :param id_sestavy: id (number)
        :rtype: list - xml responses
        """
        try:
            self.client.service.smazSestavu(idSestavy=id_sestavy)
            return self.zeep_object_to_dict()
        except Exception as e:
            raise WSDPRequestError(self.logger, e) from e


class WSDPBase(ABC):
    """Abstraktni trida vytvarejici spolecne API pro WSDP sluzby.
    Odvozene tridy musi mit property skupina_sluzeb a nazev_sluzby.
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial=False):
        self.logger = WSDPLogger(self.nazev_sluzby)
        self.client = pywsdp.create(
            self.skupina_sluzeb, self.nazev_sluzby, creds, self.logger, trial
        )
        self._trial = trial
        self._creds = creds
        self._log_adresar = self._set_default_log_dir()

    @property
    def skupina_sluzeb(self):
        """Nazev typu skupiny sluzeb - ctiOS, sestavy, vyhledat, ciselniky etc.
        Nazev musi korespondovat se slovnikem WSDL endpointu - musi byt malymi pismeny.
        """
        return self._skupina_sluzeb

    @property
    def nazev_sluzby(self):
        """Nazev sluzby, napr. ctiOS, generujCenoveUdajeDleKu.
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._nazev_sluzby

    @property
    def pristupove_udaje(self) -> dict:
        """Vraci pristupove udaje pod kterymi doslo k pripojeni ke sluzbe
        :rtype: dict
        """
        return self._creds

    @property
    def log_adresar(self) -> str:
        """Vypise cestu k adresari, ve kterem se budou vytvaret log soubory.
        :rtype: str
        """
        return self._log_adresar

    @log_adresar.setter
    def log_adresar(self, log_adresar: str):
        """Nastavi cestu k adresari, ve kterem se budou vytvaret log soubory.
        :param log_adresar: cesta k adresari
        """
        if not os.path.exists(log_adresar):
            os.makedirs(log_adresar)
        self.logger.set_directory(log_adresar)
        self._log_adresar = log_adresar

    @property
    def testovaci_mod(self) -> dict:
        """Vraci True/False podle toho zda uzivatel pristupuje k ostrym sluzbam (False)
        nebo ke sluzbam na zkousku (True)
        :rtype: bool
        """
        return self._trial

    @property
    def raw_xml(self):
        """Vraci surove XML ktere je vystupem ze sluzby, jeste nez bylo
        prevedeno na slovnik. U sluzby CtiOS vraci XML odpoved ve forme listu,
        rozdelenou po prvcich podle poctu dotazu na server.
        :rtype: list or str
        """
        return self.response_xml

    def posli_pozadavek(self, slovnik_identifikatoru: dict) -> dict:
        """Zpracuje vstupni parametry pomoci nektere ze sluzeb a
        vysledek ulozi do slovniku.
        :param slovnik: slovnik ve formatu specifickem pro danou sluzbu.
        :rtype: dict - XML odpoved rozparsovana do slovniku"
        """
        return self.client.send_request(slovnik_identifikatoru)

    def _set_default_log_dir(self) -> str:
        """Privatni metoda pro nasteveni logovaciho adresare."""

        def is_run_by_jupyter():
            import __main__ as main

            return not hasattr(main, "__file__")

        if is_run_by_jupyter():
            module_dir = os.path.abspath(
                os.path.join("../../", "pywsdp", "modules", self.nazev_sluzby)
            )
        else:
            module_dir = os.path.dirname(__file__)
        log_dir = os.path.join(module_dir, "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.logger.set_directory(log_dir)
        return log_dir


class CtiOS(WSDPBase):
    """Trida definujici rozhrani pro praci se sluzbou ctiOS.
     Vyuzivani sluzby ctiOS je na strane CUZK logovano.
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial=False):
        self._nazev_sluzby = "ctiOS"
        self._skupina_sluzeb = "ctios"
        self.input_db = None
        self.input_json = None

        super().__init__(creds, trial=trial)

    def nacti_identifikatory_z_db(self, db_path: str, sql_dotaz=None) -> dict:
        """Pripravi identifikatory z SQLITE databaze pro vstup do zavolani sluzby CtiOS.
        :param db: cesta k SQLITE databazi ziskane rozbalenim VFK souboru
        :param sql_dotaz: omezeni zpracovavanych identifikatoru pres SQL dotaz, napr. "SELECT * FROM OPSUB order by ID LIMIT 10"
        :rtype: dict
        """
        db = CtiOSDbManager(db_path, self.logger)  # pripojeni k SQLite databazi

        if sql_dotaz:
            posidents = db.get_posidents_from_db(sql_dotaz)
        else:
            posidents = db.get_posidents_from_db()

        self.input_db = db_path # zpristupneni cesty k vstupni databazi
        
        db.close_connection()
        return {"pOSIdent": posidents}

    def nacti_identifikatory_z_json_souboru(self, json_path: str) -> dict:
        """Pripravi identifikatory z JSON souboru pro vstup do zavolani sluzby CtiOS.
        Vnitrek json souboru je ve tvaru slovniku:
        {"posidents" : [pseudokod1, pseudokod2...]}.
        :param json: cesta k JSON souboru s pseudonymizovanymi identifikatory
        :rtype: dict
        """
        file = Path(json_path)
        if file.exists():
            with open(file) as f:
                data = json.load(f)
                return data
        else:
            raise WSDPError(self.logger, "File is not found!")

    def posli_pozadavek(self, slovnik_identifikatoru: dict) -> dict:
        """Zpracuje vstupni parametry pomoci nektere ze sluzeb a
        vysledek ulozi do slovniku.
        :param slovnik: slovnik ve formatu specifickem pro danou sluzbu.
        :rtype: dict - XML odpoved rozparsovana do slovniku"
        """
        response = self.client.send_request(slovnik_identifikatoru)
        self.client.log_statistics()
        return response

    def uloz_vystup(
        self, vysledny_slovnik: dict, vystupni_adresar: str, format_souboru: OutputFormat
    ):
        """Konvertuje osobni udaje typu slovnik ziskane ze sluzby CtiOS do souboru o definovanem
        formatu a soubor ulozi do definovaneho vystupniho adresare.
        :param slovnik: slovnik vraceny po zpracovani identifikatoru
        :param vystupni_adresar: cesta k vystupnimu adresari
        :param format_souboru: format typu OutputFormat.GdalDb, OutputFormat.Json nebo OutputFormat.Csv
        :rtype: str: cesta k vystupnimu souboru
        """
        cas = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
        
        if format_souboru == OutputFormat.GdalDb:
            vystupni_soubor="".join(["ctios_",cas,".db"])
            vystupni_cesta = os.path.join(vystupni_adresar, vystupni_soubor)
            shutil.copyfile(self.input_db, vystupni_cesta) # prekopirovani souboru db do cilove cesty
            db = CtiOSDbManager(vystupni_cesta, self.logger)
            db.add_column_to_db("OS_ID", "text")
            input_db_columns = db.get_columns_names()
            db_dictionary = CtiOSAttributeConverter(
                XML2DB_mapping, vysledny_slovnik, input_db_columns, self.logger
            ).convert_attributes()
            db.update_rows_in_db(db_dictionary)
            db.close_connection()
            self.logger.info("Vystup byl ulozen zde: {}".format(vystupni_cesta))
        elif format_souboru == OutputFormat.Json:
            vystupni_soubor="".join(["ctios_",cas,".json"])
            vystupni_cesta = os.path.join(vystupni_adresar, vystupni_soubor)
            with open(vystupni_cesta, "w", newline="", encoding="utf-8") as f:
                json.dump(vysledny_slovnik, f, ensure_ascii=False)
                self.logger.info("Vystup byl ulozen zde: {}".format(vystupni_cesta))
        elif format_souboru == OutputFormat.Csv:
            vystupni_soubor="".join(["ctios_",cas,".csv"])
            vystupni_cesta = os.path.join(vystupni_adresar, vystupni_soubor)
            header = sorted(
                set(i for b in map(dict.keys, vysledny_slovnik.values()) for i in b)
            )
            with open(vystupni_cesta, "w", newline="") as f:
                write = csv.writer(f)
                write.writerow(["posident", *header])
                for a, b in vysledny_slovnik.items():
                    write.writerow([a] + [b.get(i, "") for i in header])
                self.logger.info("Vystup byl ulozen zde: {}".format(vystupni_cesta))
        else:
            raise WSDPError(
                self.logger, "Format {} is not supported".format(format_souboru)
        )
        return vystupni_cesta
        

    def vypis_statistiku(self):
        """Vytiskne statistiku zpracovanych pseudonymizovanych identifikatoru (POSIdentu).
        pocet neplatnych identifikatoru = pocet POSIdentu, ktere nebylo mozne rozsifrovat;
        pocet expirovanych identifikatoru = pocet POSIdentu, kterym vyprsela casova platnost;
        pocet identifikatoru k neexistujicim OS = pocet POSIdentu, ktere obsahuji neexistujici OS ID (neni na co je napojit);
        pocet uspesne zpracovanych identifikatoru = pocet identifikatoru, ke kterym byly uspesne zjisteny osobni udaje;
        pocet odstranenych duplicit = pocet vstupnich zaznamu, ktere byly pred samotnym zpracovanim smazany z duvodu duplicit;
        pocet dotazu na server = pocet samostatnych dotazu, do kterych byl pozadavek rozdelen
        """
        self.client.print_statistics()


class SestavyBase(WSDPBase):
    """Abstraktni trida definujici rozhrani pro praci se sestavami
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial=True):
        self._skupina_sluzeb = "sestavy"

        super().__init__(creds, trial=trial)

    @property
    @abstractmethod
    def nazev_sluzby(self):
        """Nazev sluzby, napr. generujCenoveUdajeDleKu.
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """

    @property
    def skupina_sluzeb(self):
        """Nazev typu skupiny sluzeb - ctiOS, sestavy, vyhledat, ciselniky etc.
        Nazev musi korespondovat se slovnikem WSDL endpointu - musi byt malymi pismeny.
        """
        return self._skupina_sluzeb

    def nacti_identifikatory_z_json_souboru(self, json_path: str) -> dict:
        """Pripravi identifikatory z JSON souboru pro vstup do zavolani sluzby ze skupiny WSDP sestavy.
        :param json_path: cesta ke vstupnimu json souboru
        :rtype: dict
        """
        file = Path(json_path)
        if file.exists():
            with open(file) as f:
                data = json.load(f)
                return data
        else:
            raise WSDPError(self.logger, "Soubor nebyl nalezen!")

    def vypis_info_o_sestave(self, sestava: dict) -> dict:
        """S parametrem id sestavy zavola sluzbu SeznamSestav, ktera vypise info o sestave.
        :param sestava: slovnik vraceny pri vytvoreni sestavy
        :rtype: slovnik ve tvaru {'zprava': '',
         'idSestavy': '',
         'nazev': '',
         'pocetJednotek': '',
         'pocetStran': '',
         'cena': '',
         'datumPozadavku': '',
         'datumSpusteni': '',
         'datumVytvoreni': '',
         'stav': '',
         'format': '',
         'elZnacka': ''}
        """
        service = "seznamSestav"
        seznam_sestav = pywsdp.create(
            self._skupina_sluzeb,
            service,
            self.pristupove_udaje,
            self.logger,
            self.testovaci_mod,
        )
        return seznam_sestav.send_request(sestava["idSestavy"])

    def zauctuj_sestavu(self, sestava: dict) -> dict:
        """Vezme id sestavy z vytvorene sestavy a zavola sluzbu VratSestavu, ktera danou sestavu zauctuje.
        :param sestava: slovnik vraceny pri vytvoreni sestavy
        :rtype: slovnik ve tvaru {'zprava': '',
         'idSestavy': '',
         'nazev': '',
         'pocetJednotek': '',
         'pocetStran': '',
         'cena': '',
         'datumPozadavku': '',
         'datumSpusteni': '',
         'datumVytvoreni': '',
         'stav': '',
         'format': '',
         'elZnacka': '',
         'souborSestavy': ''}
        """
        service = "vratSestavu"
        vrat_sestavu = pywsdp.create(
            self._skupina_sluzeb,
            service,
            self.pristupove_udaje,
            self.logger,
            self.testovaci_mod,
        )
        return vrat_sestavu.send_request(sestava["idSestavy"])

    def vymaz_sestavu(self, sestava: dict) -> dict:
        """Vezme id sestavy z vytvorene sestavy a zavola sluzbu SmazSestavu, ktera danou sestavu z uctu smaze.
        :param sestava: slovnik vraceny pri vytvoreni sestavy
        :rtype: slovnik ve tvaru {'zprava': ''}
        """
        service = "smazSestavu"
        smaz_sestavu = pywsdp.create(
            self._skupina_sluzeb,
            service,
            self.pristupove_udaje,
            self.logger,
            self.testovaci_mod,
        )
        return smaz_sestavu.send_request(sestava["idSestavy"])


class GenerujCenoveUdajeDleKu(SestavyBase):
    """Trida definujici rozhrani pro praci se sluzbou Generuj cenove udaje dle katastralnich uzemi
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial=True):
        self._nazev_sluzby = "generujCenoveUdajeDleKu"

        super().__init__(creds, trial=trial)

    @property
    def nazev_sluzby(self):
        """Nazev sluzby, napr. ctiOS, generujCenoveUdajeDleKu.
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._nazev_sluzby

    def uloz_vystup(self, zauctovana_sestava: dict, vystupni_adresar: str) -> str:
        """Rozkoduje soubor z vystupnich hodnot sluzby VratSestavu a ulozi ho na disk.
        :param zauctovana_sestava: slovnik vraceny po zauctovani sestavy
        :rtype: string - cesta k vystupnimu souboru
        """
        import base64

        datum = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
        vystupni_soubor = "cen_udaje_{}.{}".format(datum, zauctovana_sestava["format"])
        vystupni_cesta = os.path.join(vystupni_adresar, vystupni_soubor)
        binary = base64.b64decode(zauctovana_sestava["souborSestavy"])
        with open(vystupni_cesta, "wb") as f:
            f.write(binary)
            self.logger.info("Vystupni soubor je k dispozici zde: {}".format(vystupni_cesta))
        return vystupni_cesta


class SeznamSestav(WSDPBase):
    """Trida definujici rozhrani pro praci se sluzbou Seznam sestav.
    Pouzije se v pripade, kdy znam sestavu a chci tuto sluzbu zavolat samostatne.
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial=True):
        self._nazev_sluzby = "seznamSestav"
        self._skupina_sluzeb = "sestavy"

        super().__init__(creds, trial=trial)

    @property
    def nazev_sluzby(self):
        """
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._nazev_sluzby

    @property
    def skupina_sluzeb(self):
        """
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._skupina_sluzeb


class VratSestavu(WSDPBase):
    """Trida definujici rozhrani pro praci se sluzbou Vrat sestavu.
    Pouzije se v pripade, kdy znam sestavu a chci tuto sluzbu zavolat samostatne.
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial=True):
        self._nazev_sluzby = "vratSestavu"
        self._skupina_sluzeb = "sestavy"

        super().__init__(creds, trial=trial)

    @property
    def nazev_sluzby(self):
        """
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._nazev_sluzby

    @property
    def skupina_sluzeb(self):
        """
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._skupina_sluzeb
    

class SmazSestavu(WSDPBase):
    """Trida definujici rozhrani pro praci se sluzbou Smaz sestavu.
    Pouzije se v pripade, kdy znam sestavu a chci tuto sluzbu zavolat samostatne.
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial=True):
        self._nazev_sluzby = "smazSestavu"
        self._skupina_sluzeb = "sestavy"

        super().__init__(creds, trial=trial)

    @property
    def nazev_sluzby(self):
        """
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._nazev_sluzby

    @property
    def skupina_sluzeb(self):
        """
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._skupina_sluzeb

    
if __name__ == "__main__":

    creds_test = ["WSTEST", "WSHESLO"]

    ctios = CtiOS(creds_test, trial=True)
    # parametry = {
    #     "pOSIdent": [
    #         "im+o3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q=",
    #         "4m3Yuf1esDMzbgNGYW7kvzjlaZALZ3v3D7cXmxgCcFp0RerVtxqo8yb87oI0FBCtp49AycQ5NNI3vl+b+SEa+8SfmGU4sqBPH2pX/76wyBI=",
    #         "5wQRil9Nd5KIrn5KWTf8+sksZslnMqy2tveDvYPIsd1cd9qHYs1V9d9uZVwBEVe5Sknvonhh+FDiaYEJa+RdHM3VtvGsIqsc2Hm3mX0xYfs=",
    #         "UKcYWvUUTpNi8flxUzlm+Ss5iq0JV3CiStJSAMOk6xHFQncZraFeO9yj8OGraKiDJ8eLB0FegdXYuyYWsEXiv2H9ws95ezlKNTqR6ze7aOnR3a7NWzWJfe+R5VHfU13+",
    #     ]
    # }
    # json_path = os.path.abspath(
    #   os.path.join(os.path.dirname(__file__), "data", "input", "ctios_template_all.json")
    # )
    # parametry = ctios.nacti_identifikatory_z_json_souboru(json_path)
    # print("parametryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
    # print(parametry)

    db_path = os.path.abspath(
      os.path.join(os.path.dirname(__file__), "data", "input", "ctios_template.db")
    )
    parametry = ctios.nacti_identifikatory_z_db(db_path)
    print("parametryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
    print(parametry)
    print(ctios.log_adresar)
    
    slovnik = ctios.posli_pozadavek(parametry)
    # print(slovnik)

    vystupni_adresar = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "data", "output")
      )

    vystup = ctios.uloz_vystup(slovnik, vystupni_adresar, OutputFormat.Json)
    vystup = ctios.uloz_vystup(slovnik, vystupni_adresar, OutputFormat.Csv)
    vystup = ctios.uloz_vystup(slovnik, vystupni_adresar, OutputFormat.GdalDb)
    ctios.vypis_statistiku()


    # Generuj cenove udaje dle ku
    gen = GenerujCenoveUdajeDleKu(creds_test, trial=True)
    parametry = {
        "katastrUzemiKod": 732630,
        "rok": 2020,
        "mesicOd": 9,
        "mesicDo": 12,
        "format": "zip",
    }

    ses = gen.posli_pozadavek(parametry)
    print(ses)

    # # Seznam sestav
    # info = gen.vypis_info_o_sestave(ses)
    # #print(info)

    # # Vrat sestavu
    # zauctovani = gen.zauctuj_sestavu(ses)
    # #print(zauctovani)

    # # Smaz sestavu
    # smazani = gen.vymaz_sestavu(ses)
    # #print(smazani)

    # cesta = gen.uloz_vystup(zauctovani, vystupni_adresar)
    # print(cesta)
    
    seznam = SeznamSestav(creds_test, trial=True)
    slovnik = seznam.posli_pozadavek(ses["idSestavy"])
    print(slovnik)
    
    vrat = VratSestavu(creds_test, trial=True)
    slovnik = vrat.posli_pozadavek(ses["idSestavy"])
    print(slovnik)
    
    smaz = SmazSestavu(creds_test, trial=True)
    slovnik = smaz.posli_pozadavek(ses["idSestavy"])
    print(slovnik)