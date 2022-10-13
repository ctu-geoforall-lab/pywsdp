import os
import re
import csv
import math
from abc import ABC, abstractmethod
import json
import sqlite3
from pathlib import Path
import xml.etree.ElementTree as et
import logging
from datetime import datetime

from zeep import Client, Settings, helpers
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken

from enum import Enum
 
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
	"idNadrizenePravnickeOsoby": "ID_NADRIZENE_PO"
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

        file_handler = logging.FileHandler(
            filename=log_dir + "/" + log_filename, mode="w"
        )

        formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.addHandler(file_handler)


xmlNamespace0 = {"sestavy": "{http://katastr.cuzk.cz/sestavy/types/v2.9}",
                 "ctios": "{http://katastr.cuzk.cz/ctios/types/v2.8}" }

xmlNamespace1 = {"sestavy": "{http://katastr.cuzk.cz/commonTypes/v2.9}",
                 "ctios": "{http://katastr.cuzk.cz/commonTypes/v2.8}"}

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


class WSDPClient(ABC):

  @classmethod
  def _from_recipe(cls, wsdl, service_name, creds, logger, trial):
    """
    Method used by factory for creating instances of WSDP client classes.
    :param wsdl: link to wsdl document (str)
    :param service_name: name of the service used in CUZK documentation (str)
    :param creds: credentials to WSDP (dict)
    :rtype: Cient class
    """
    result = cls()
    if trial == True:
        result.client = Client(trialWsdls[wsdl],
    					transport=transport,
    					wsse=UsernameToken(*creds),
    					settings=settings,
    				)
    else:
        result.client = Client(prodWsdls[wsdl],
    					transport=transport,
    					wsse=UsernameToken(*creds),
    					settings=settings,
    				)			
    result.service_name = service_name
    result.logger = WSDPLogger(service_name)
    result.creds = creds
    return result

  @abstractmethod
  def send_request(*args):
    """
    Method for sending a request to a service. Must be defined by all child classes.
    """
    pass


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
    print(*args)
    return cls._from_recipe(*args)


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
    """Class parsing ctiOS XML response into a dictionary.
    """

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
            logger.info(os_tag.text)

        # Find all tags with 'report' name
        namespace_ns0 = xmlNamespace0["sestavy"]
        for os_tag in root.findall(".//{}report".format(namespace_ns0)):

            # Id sestavy
            xml_dict["idSestavy"] = os_tag.find("{}id".format(namespace_ns0)).text
            if xml_dict["idSestavy"]:
                logger.info("ID sestavy: {}".format(xml_dict["idSestavy"]))
            else:
                raise WSDPResponseError(
                    logger,
                    "ID sestavy nebylo vraceno")

            # Nazev sestavy
            if os_tag.find("{}nazev".format(namespace_ns0)) is not None:
                xml_dict["nazev"] = os_tag.find("{}nazev".format(namespace_ns0)).text
                logger.info("Nazev sestavy: {}".format(xml_dict["nazev"]))

            # Pocet jednotek
            if os_tag.find("{}pocetJednotek".format(namespace_ns0)) is not None:
                xml_dict["pocetJednotek"] = os_tag.find("{}pocetJednotek".format(namespace_ns0)).text
                logger.info("Pocet jednotek: {}".format(xml_dict["pocetJednotek"]))

            # Pocet stran
            if os_tag.find("{}pocetStran".format(namespace_ns0)) is not None:
                xml_dict["pocetStran"] = os_tag.find("{}pocetStran".format(namespace_ns0)).text
                logger.info("Pocet stran: {}".format(xml_dict["pocetStran"]))

            # Cena
            if os_tag.find("{}cena".format(namespace_ns0)) is not None:
                xml_dict["cena"] = os_tag.find("{}cena".format(namespace_ns0)).text
                logger.info("Cena: {}".format(xml_dict["cena"]))

            # Datum pozadavku
            if os_tag.find("{}datumPozadavku".format(namespace_ns0)) is not None:
                xml_dict["datumPozadavku"] = os_tag.find("{}datumPozadavku".format(namespace_ns0)).text
                logger.info("Datum pozadavku: {}".format(xml_dict["datumPozadavku"]))

            # Datum spusteni
            if os_tag.find("{}datumSpusteni".format(namespace_ns0)) is not None:
                xml_dict["datumSpusteni"] = os_tag.find("{}datumSpusteni".format(namespace_ns0)).text
                logger.info("Datum spusteni: {}".format(xml_dict["datumSpusteni"]))

            # Datum vytvoreni
            if os_tag.find("{}datumVytvoreni".format(namespace_ns0))is not None:
                xml_dict["datumVytvoreni"] = os_tag.find("{}datumVytvoreni".format(namespace_ns0)).text
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
                xml_dict["elZnacka"] = os_tag.find("{}elZnacka".format(namespace_ns0)).text
                logger.info("Elektronicka znacka: {}".format(xml_dict["elZnacka"]))

            # Soubor sestavy
            if os_tag.find("{}souborSestavy".format(namespace_ns0)) is not None:
                xml_dict["souborSestavy"] = os_tag.find("{}souborSestavy".format(namespace_ns0)).text

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
                                "XML attribute name cannot be converted to database column name"
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
        self.schema = "OPSUB" # schema containning info about posidents
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
            raise WSDPError(self.logger, e)

    def _create_connection(self):
        """
        Create a database connection to the SQLite database specified by the db_path
        Raises:
            WSDPError: SQLite error
        """

        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise WSDPError(self.logger, e)

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
            raise WSDPError(self.logger, e)

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
            raise WSDPError(self.logger, e)

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
            raise WSDPError(self.logger, e)

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
                        """UPDATE TABLE {0} SET {1} = ? WHERE id = ?""".format(self.schema, dat_name),
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
    
    
@pywsdp.register
class CtiOsClient(WSDPClient):
  """
  Client for communicating with CtiOS WSDP service. 
  """
  service_name = "ctiOS"
  service_group = "ctios" 
    
  def __init__(self):
    super().__init__()
    self.posidents_per_request = 10 # Set max number of posidents per request
    self.number_of_posidents = 0
    self.number_of_posidents_final = 0
  
  def send_request(self, dictionary):
    """
    Send the request in the form of dictionary and get the response.
    Raises:
        WSDPRequestError: Zeep library request error
    :param dictionary: input service attributes
    :rtype: list - xml responses divided based on chunks
    """
    
    def create_chunks(lst, n):
        """"Create n-sized chunks from list as a generator"""
        n = max(1, n)
        return (lst[i : i + n] for i in range(0, len(lst), n))

    # Save statistics
    self.number_of_posidents = len(dictionary["pOSIdent"])
        
    # Remove duplicates
    posidents = list(dict.fromkeys(dictionary["pOSIdent"]))
    self.number_of_posidents_final = len(posidents)
        
    # create chunks
    chunks = create_chunks(posidents, self.posidents_per_request)
    
    # process posident chunks and return xml response as the list
    response_xml_list = []
    for chunk in chunks:
        try:
            response_xml = self.client.service.ctios(pOSIdent=chunk)
        except:
            raise WSDPRequestError
        response_xml_list.append(response_xml)
    return response_xml_list


@pywsdp.register
class GenerujCenoveUdajeDleKuClient(WSDPClient):
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
    :rtype: list - xml responses
    """
    try:
        return self.client.service.generujCenoveUdajeDleKu(katastrUzemiKod=dictionary["katastrUzemiKod"],
                                                           rok=dictionary["rok"],
                                                           mesicOd=dictionary["mesicOd"],
                                                           mesicDo=dictionary["mesicDo"],
                                                           format=dictionary["format"])
    except:
        raise WSDPRequestError

@pywsdp.register
class SeznamSestavClient(WSDPClient):
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
        return self.client.service.seznamSestav(idSestavy=id_sestavy)
    except:
        raise WSDPRequestError
    
@pywsdp.register
class VratSestavuClient(WSDPClient):
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
        return self.client.service.vratSestavu(idSestavy=id_sestavy)
    except:
        raise WSDPRequestError

@pywsdp.register
class SmazSestavuClient(WSDPClient):
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
      return self.client.service.smazSestavu(idSestavy=id_sestavy)
    except:
        raise WSDPRequestError   
 

class WSDPBase(ABC):
    """Abstraktni trida vytvarejici spolecne API pro WSDP sluzby.
       Odvozene tridy musi mit property skupina_sluzeb a nazev_sluzby.
       :param creds: slovnik pristupovych udaju [uzivatel, heslo]
       :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """    
    def __init__(self, creds: dict, trial = False):
        self.logger = WSDPLogger(self.nazev_sluzby)
        self.client = pywsdp.create(self.skupina_sluzeb, self.nazev_sluzby, creds, self.logger, trial)
        self._trial = trial
        self._creds = creds
        self._log_adresar = self._set_default_log_dir()

    @property
    @abstractmethod
    def skupina_sluzeb(self):
        """Nazev typu skupiny sluzeb - ctiOS, sestavy, vyhledat, ciselniky etc.
           Nazev musi korespondovat se slovnikem WSDL endpointu - musi byt malymi pismeny.
        """
        pass
            
    @property
    @abstractmethod
    def nazev_sluzby(self):
        """Nazev sluzby, napr. ctiOS, generujCenoveUdajeDleKu.
           Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        pass
                
    @property    
    def pristupove_udaje(self) -> dict:
        """Vraci pristupove udaje pod kterymi doslo k pripojeni ke sluzbe
        :rtype: dict
        """
        return self._creds

    @property
    def log_adresar(self) -> str:
        """ Vypise cestu k adresari, ve kterem se budou vytvaret log soubory.
        :rtype: str
        """
        return self._log_adresar
        
    @log_adresar.setter
    def log_adresar(self, log_adresar: str):
        """Nastavi cestu k adresari, ve kterem se budou vytvaret log soubory.        
        :param log_adresar: cesta k adresari
        """
        if not os.path.exists( log_adresar):
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
    
    def posli_pozadavek(self, slovnik_identifikatoru: dict) -> str:
        """Zpracuje vstupni parametry pomoci sluzby CtiOS a vysledne osobni udaje
        opravnenych subjektu ulozi do slovniku.
        :param slovnik: slovnik ve formatu: {"posidents" : [pseudokod1, pseudokod2...]}.
        :rtype: str - XML response"
        """
        return self.client.send_request(slovnik_identifikatoru)

    def _set_default_log_dir(self) ->  str:
        """Privatni metoda pro nasteveni logovaciho adresare.
        """
        def is_run_by_jupyter():
            import __main__ as main
            return not hasattr(main, '__file__')

        if is_run_by_jupyter():
            module_dir = os.path.abspath(os.path.join('../../', 'pywsdp', 'modules', self.nazev_sluzby))
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
    def __init__(self, creds: dict, trial = False):
        self._nazev_sluzby = "ctiOS"
        self._skupina_sluzeb = "ctios"
        
        super().__init__(creds, trial=trial)
        
        self.counter = CtiOSCounter() # inicializace citace, ktery pocita pocty typu zpracovanych posidentu

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
    
    def nacti_identifikatory_z_db(self, db_path: str, sql_dotaz=None) -> dict:
        """Pripravi identifikatory z SQLITE databaze pro vstup do zavolani sluzby CtiOS.
        :param db: cesta k SQLITE databazi ziskane rozbalenim VFK souboru
        :param sql_dotaz: omezeni zpracovavanych identifikatoru pres SQL dotaz, napr. "SELECT * FROM OPSUB order by ID LIMIT 10"
        :rtype: dict
        """
        db = CtiOSDbManager(db_path, self.logger) # pripojeni k SQLite databazi
        
        if sql_dotaz:
            posidents = db.get_posidents_from_db(sql_dotaz)
        else:
            posidents = db.get_posidents_from_db()

        db.close_connection()
        return posidents
    
    def nacti_identifikatory_z_json_souboru(self, json: str) -> dict:
        """Pripravi identifikatory z JSON souboru pro vstup do zavolani sluzby CtiOS.
        Vnitrek json souboru je ve tvaru slovniku:
        {"posidents" : [pseudokod1, pseudokod2...]}.
        :param json: cesta k JSON souboru s pseudonymizovanymi identifikatory
        :rtype: dict
        """
        file = Path(json)
        if file.exists():
            with open(file) as f:
                data = json.load(f)
                return data["posidents"]
        else:
            raise WSDPError(
                self.logger,
                "File is not found!"
                )
    
    def preved_vysledek_na_slovnik(self, xml_response: list) -> dict:
        """Prevede XML odpoved ze sluzby na slovnik.
        :param xml_response: odpoved sluzby jako XML ve formatu str
        :rtype: dict - atributy z XML odpovedi prevedeny do slovniku"
        """
        dictionary = {}
        for item in xml_response:
            partial_dictionary = helpers.serialize_object(item, dict)
            dictionary = {**dictionary, **partial_dictionary}
        return dictionary
        
        
    def uloz_vystup(self, vysledny_slovnik: dict, vystupni_soubor: str, format_souboru: OutputFormat):
        """Konvertuje osobni udaje typu slovnik ziskane ze sluzby CtiOS do souboru o definovanem
        formatu a soubor ulozi do definovaneho vystupniho adresare.
        :param slovnik: slovnik vraceny po zpracovani identifikatoru
        :param vystupni_soubor: cesta k vystupnimu souboru
        :param format_souboru: format typu OutputFormat.GdalDb, OutputFormat.Json nebo OutputFormat.Csv
        """
        if format_souboru == OutputFormat.GdalDb:
            db = CtiOSDbManager(vystupni_soubor, self.logger)
            db.add_column_to_db("OS_ID", "text")
            input_db_columns = db.get_columns_names()
            db_dictionary =  CtiOSAttributeConverter(XML2DB_mapping, vysledny_slovnik, input_db_columns, self.logger).convert_attributes()
            db.save_attributes_to_db(db_dictionary)
            db.close_connection()            
            self.logger.info(
                    "Soubor v ceste {} byl aktualizovan.".format(vystupni_soubor)
            )            
        elif format_souboru == OutputFormat.Json:
            with open(vystupni_soubor, "w", newline="", encoding='utf-8') as f:
                json.dump(vysledny_slovnik, f, ensure_ascii=False)
                self.logger.info(
                        "Vystup byl ulozen zde: {}".format(vystupni_soubor)
                )
        elif format_souboru == OutputFormat.Csv:
            header = sorted(set(i for b in map(dict.keys, vysledny_slovnik.values()) for i in b))
            with open(vystupni_soubor, "w", newline="") as f:
                write = csv.writer(f)
                write.writerow(["posident", *header])
                for a, b in vysledny_slovnik.items():
                    write.writerow([a] + [b.get(i, "") for i in header])
                self.logger.info(
                        "Vystup byl ulozen zde: {}".format(vystupni_soubor)
                )
        else:
            raise WSDPError(
                self.logger,
                "Format {} is not supported".format(format_souboru)
            )
        
    def vypis_statistiku(self):
        """Vytiskne statistiku zpracovanych pseudonymizovanych identifikatoru (POSIdentu).
            pocet neplatnych identifikatoru = pocet POSIdentu, ktere nebylo mozne rozsifrovat;
            pocet expirovanych identifikatoru = pocet POSIdentu, kterym vyprsela casova platnost;
            pocet identifikatoru k neexistujicim OS = pocet POSIdentu, ktere obsahuji neexistujici OS ID (neni na co je napojit);
            pocet uspesne zpracovanych identifikatoru = pocet identifikatoru, ke kterym byly uspesne zjisteny osobni udaje;
            pocet odstranenych duplicit = pocet vstupnich zaznamu, ktere byly pred samotnym zpracovanim smazany z duvodu duplicit;
            pocet dotazu na server = pocet samostatnych dotazu, do kterych byl pozadavek rozdelen
        """
        print( {"celkovy pocet identifikatoru na vstupu": self.ctios.number_of_posidents,
                "pocet odstranenych duplicit": self.ctios.number_of_posidents -self.ctios.number_of_posidents_final,
                "pocet dotazu na server":  math.ceil(self.ctios.number_of_posidents_final / self.ctios.posidents_per_request),
                "pocet uspesne zpracovanych identifikatoru": self.counter.uspesne_stazeno,
                "pocet neplatnych identifikatoru": self.counter.neplatny_identifikator,
                "pocet expirovanych identifikatoru": self.counter.expirovany_identifikator,
                "pocet identifikatoru k neexistujicim OS": self.counter.opravneny_subjekt_neexistuje} )
 
    def zaloguj_statistiku(self):
        """Yaloguje statistiku zpracovanych pseudonymizovanych identifikatoru (POSIdentu)."""
        self.logger.info(
            "Celkovy pocet dotazovanych identifikatoru na vstupu: {}".format(self.ctios.number_of_posidents)
        )
        self.logger.info(
            "Pocet odstranenych duplicitnich identifikatoru: {}".format(
                self.ctios.number_of_posidents - self.ctios.number_of_posidents_final
            )
        )
        self.logger.info(
            "Pocet pozadavku, do kterych byl dotaz rozdelen (pocet dotazu na server): {}".format(
                math.ceil(self.ctios.number_of_posidents_final / self.ctios.posidents_per_request)
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

            
class SestavyBase(WSDPBase):
    """Abstraktni trida definujici rozhrani pro praci se sestavami
        :param creds: slovnik pristupovych udaju [uzivatel, heslo]
        :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """
    def __init__(self, creds: dict, trial = True):
        self._skupina_sluzeb = "sestavy"
        
        super().__init__(creds, trial=trial)

    @property
    @abstractmethod
    def nazev_sluzby(self):
        """Nazev sluzby, napr. generujCenoveUdajeDleKu.
           Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        pass

    @property
    def skupina_sluzeb(self):
        """Nazev typu skupiny sluzeb - ctiOS, sestavy, vyhledat, ciselniky etc.
           Nazev musi korespondovat se slovnikem WSDL endpointu - musi byt malymi pismeny.
        """
        return self._skupina_sluzeb
            
    def nacti_identifikatory_z_json_souboru(self, json: str) -> dict:
        """Pripravi identifikatory z JSON souboru pro vstup do zavolani sluzby ze skupiny WSDP sestavy.
        :rtype: dict
        """
        file = Path(json)
        if file.exists():
            with open(file) as f:
                data = json.load(f)
                return data
        else:
            raise WSDPError(
                self.logger,
                "File is not found!"
                )
            
    def preved_vysledek_na_slovnik(self, xml_response: str) -> dict:
        """Prevede XML odpoved ze sluzby na slovnik
        :param xml_response: odpoved sluzby jako XML ve formatu str
        :rtype: dict - atributy z XML odpovedi prevedeny do slovniku"
        """
        return SestavyXMLParser()(
           content=xml_response, logger=self.logger
        )

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
        seznamSestav = pywsdp.create("sestavy", "seznamSestav", self.pristupove_udaje, self.logger, trial=self.testovaci_mod)
        xml_response = seznamSestav.send_request(sestava["idSestavy"])
        return self.preved_vysledek_na_slovnik(xml_response)

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
         'souborSestavy': ''}"""
        vratSestavu = pywsdp.create("sestavy", "vratSestavu", self.pristupove_udaje, self.logger, trial=self.testovaci_mod)
        xml_response = vratSestavu.send_request(sestava["idSestavy"])
        return self.preved_vysledek_na_slovnik(xml_response)

    def vymaz_sestavu(self, sestava: dict) -> dict:
        """Vezme id sestavy z vytvorene sestavy a zavola sluzbu SmazSestavu, ktera danou sestavu z uctu smaze.
        :param sestava: slovnik vraceny pri vytvoreni sestavy
        :rtype: slovnik ve tvaru {'zprava': ''}
        """
        smazSestavu = pywsdp.create("sestavy", "smazSestavu", self.pristupove_udaje, self.logger, trial=self.testovaci_mod)
        xml_response = smazSestavu.send_request(sestava["idSestavy"])
        return self.preved_vysledek_na_slovnik(xml_response)
                                
                        
class GenerujCenoveUdajeDleKu(SestavyBase):
    """Trida definujici rozhrani pro praci se sluzbou Generuj cenove udaje dle katastralnich uzemi
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """    
    def __init__(self, creds: dict, trial = True):
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
        output = os.path.join(vystupni_adresar, vystupni_soubor)       
        binary = base64.b64decode(zauctovana_sestava["souborSestavy"])
        with open(output, 'wb') as f:
            f.write(binary)
            self.logger.info(
                    "Vystupni soubor je k dispozici zde: {}".format(output)
            )


if __name__ == "__main__":

    creds_test = ["WSTEST", "WSHESLO"]
    
    # CtiOS
    ctios = CtiOS(creds_test, trial=True)
    print(ctios)
    print(ctios.skupina_sluzeb)
    print(ctios.nazev_sluzby)
    print(ctios.pristupove_udaje)
    print(ctios.log_adresar)
    print(ctios.testovaci_mod)
    parametry = {"pOSIdent": ["im+o3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q=",
                              "4m3Yuf1esDMzbgNGYW7kvzjlaZALZ3v3D7cXmxgCcFp0RerVtxqo8yb87oI0FBCtp49AycQ5NNI3vl+b+SEa+8SfmGU4sqBPH2pX/76wyBI=",
                              "5wQRil9Nd5KIrn5KWTf8+sksZslnMqy2tveDvYPIsd1cd9qHYs1V9d9uZVwBEVe5Sknvonhh+FDiaYEJa+RdHM3VtvGsIqsc2Hm3mX0xYfs=",
                              "UKcYWvUUTpNi8flxUzlm+Ss5iq0JV3CiStJSAMOk6xHFQncZraFeO9yj8OGraKiDJ8eLB0FegdXYuyYWsEXiv2H9ws95ezlKNTqR6ze7aOnR3a7NWzWJfe+R5VHfU13+"]}
    
    xml_odpoved = ctios.posli_pozadavek(parametry)
    print(xml_odpoved)
    print(type(xml_odpoved))
    slovnik = ctios.preved_vysledek_na_slovnik(xml_odpoved)
    print(slovnik)    

    print(os.path.dirname( __file__ ))
    vystupni_soubor = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data', 'output', 'ctios.json'))
    ctios.uloz_vystup(slovnik, vystupni_soubor , OutputFormat.Json)

    # vystupni_soubor = os.path.join('../', 'data', 'output', 'ctios.json')
    # ctios.uloz_vystup(slovnik, vystupni_soubor , OutputFormat.Json)
    
    # Generuj cenove udaje dle ku
    # gen = GenerujCenoveUdajeDleKu(creds_test, trial=True)
    # print(gen)
    # print(gen.skupina_sluzeb)
    # print(gen.nazev_sluzby)
    # print(gen.pristupove_udaje)
    # print(gen.log_adresar)
    # print(gen.testovaci_mod)
    
    # parametry = {"katastrUzemiKod": 732630,
    #               "rok": 2020,
    #               "mesicOd": 9,
    #               "mesicDo": 12,
    #               "format": "zip"}
    
    # xml_odpoved = gen.posli_pozadavek(parametry)
    # print(xml_odpoved)
    # sestava = gen.preved_vysledek_na_slovnik(xml_odpoved)
    # print(sestava) 
    
    # # Seznam sestav
    # xml_info = gen.vypis_info_o_sestave(sestava)
    # print(xml_info)
    # info = gen.preved_vysledek_na_slovnik(xml_info)
    # print(info) 

    # # Vrat sestavu
    # xml_info = gen.zauctuj_sestavu(sestava)
    # print(xml_info)
    # info = gen.preved_vysledek_na_slovnik(xml_info)
    # print(info) 

    # # Smaz sestavu
    # xml_info = gen.smaz_sestavu(sestava)
    # print(xml_info)
    # info = gen.preved_vysledek_na_slovnik(xml_info)
    # print(info) 