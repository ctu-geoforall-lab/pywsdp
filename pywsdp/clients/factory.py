"""
@package clients

@brief Factory class for WSDP services

Classes:
 - factory::ClientFactory
 - factory::WSDPClient
 - factory::SestavyClient
 - factory::CtiOsClient
 - factory::GenerujCenoveUdajeDleKuClient
 - factory::SeznamSestavClient
 - factory::VratSestavuClient
 - factory::SmazSestavuClient

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import math
from lxml import etree
from abc import ABC, abstractmethod
from zeep import Client, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
from zeep.plugins import HistoryPlugin

from pywsdp.base.exceptions import WSDPRequestError
from pywsdp.base.globalvars import trialWsdls, prodWsdls
from pywsdp.clients.helpers.ctiOS import XMLParser as CtiOSParser
from pywsdp.clients.helpers.ctiOS import Counter
from pywsdp.clients.helpers.generujCenoveUdajeDleKu import XMLParser as SestavyParser


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
        return SestavyParser()(content=response_xml, logger=self.logger)


class ClientFactory:
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


pywsdp = ClientFactory()


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
        self.parser = CtiOSParser()
        self.counter = Counter() # Counts statistics
        
        
    def send_request(self, dictionary):
        """
        Send the request in the form of dictionary and get the response.
        Raises:
            WSDPRequestError: Zeep library request error
        :param dictionary: input service attributes
        :rtype: tuple (dict - xml response, dict - errorneous posidents)
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
        response_dict_errors = {}
        for chunk in chunks:
            try:
                self.client.service.ctios(pOSIdent=chunk)
                item = self.zeep_object_to_xml()
            except Exception as e:
                raise WSDPRequestError(self.logger, e) from e

            # save to raw xml list
            self.response_xml.append(item)

            # create response dictionary
            partial_dictionary, partial_dictionary_errors = self.parser(
                content=item, counter=self.counter, logger=self.logger
            )
            response_dict = {**response_dict, **partial_dictionary}
            response_dict_errors = {**response_dict_errors, **partial_dictionary_errors}
        return response_dict, response_dict_errors

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