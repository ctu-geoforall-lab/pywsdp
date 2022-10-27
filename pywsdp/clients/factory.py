"""
@package clients

@brief Factory class for WSDP services

Classes:
 - factory::WSDPClient
 - factory::ClientFactory
 - factory::CtiOsClient
 - factory::GenerujCenoveUdajeDleKuClient
 - factory::SeznamSestavClient
 - factory::VratSestavuClient
 - factory::SmazSestavuClient

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import math
from abc import ABC, abstractmethod
from zeep import Client, Settings, helpers
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
from zeep.plugins import HistoryPlugin

from pywsdp.base.exceptions import WSDPRequestError
from pywsdp.clients.helpers.ctiOS import DictEditor as CtiOSDict
from pywsdp.clients.helpers.ctiOS import Counter
from pywsdp.clients.helpers.generujCenoveUdajeDleKu import (
    DictEditor as SestavyDict,
)


transport = Transport(cache=SqliteCache())
settings = Settings(raw_response=False, strict=False, xml_huge_tree=True)
settings = Settings(strict=False, xml_huge_tree=True)
history = HistoryPlugin()


# WSDL endpoints
_trialWsdls = {
    "sestavy": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/sestavy_v29.wsdl",
    "ctios": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws28/ctios/ctios_v28.wsdl",
}

_prodWsdls = {
    "sestavy": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/sestavy_v29.wsdl",
    "ctios": "https://katastr.cuzk.cz/dokumentace/ws28/ctios/ctios_v28.wsdl",
}


class WSDPClient(ABC):
    """
    Abstract class creating interface for all WSDP clients.
    """

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
        try:
            if trial is True:
                result.client = Client(
                    _trialWsdls[wsdl],
                    transport=transport,
                    wsse=UsernameToken(*creds),
                    settings=settings,
                    plugins=[history],
                )
            else:
                result.client = Client(
                    _prodWsdls[wsdl],
                    transport=transport,
                    wsse=UsernameToken(*creds),
                    settings=settings,
                    plugins=[history],
                )
        except Exception as exc:
            raise WSDPRequestError(logger, exc) from exc

        result.service_name = service_name
        result.logger = logger
        result.creds = creds
        return result

    @abstractmethod
    def send_request(self, *args):
        """
        Method for sending a request to a service. Must be defined by all child classes.
        """


class ClientFactory:
    """
    Factory for creating WSDP clients.
    """

    def __init__(self):
        self.classes = {}

    def register(self, cls):
        """
        Register class clients to factory.
        """
        self.classes[cls.service_name] = cls
        return cls

    def create(self, *args):
        """
        Create instances of client objects.
        """
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
        self.counter = Counter()  # Counts statistics

    def send_request(self, dictionary):
        """
        Send the request in the form of dictionary and get the response.
        Raises:
            WSDPRequestError: Zeep library request error
        :param dictionary: input service attributes
        :rtype: tuple (dict - xml response, dict - errorneous posidents)
        """

        def create_chunks(lst, chunk_size):
            """ "Create n-sized chunks from list as a generator"""
            chunk_size = max(1, chunk_size)
            return (lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size))

        # Save statistics
        self.number_of_posidents = len(dictionary["pOSIdent"])

        # Remove duplicates
        posidents = list(dict.fromkeys(dictionary["pOSIdent"]))
        self.number_of_posidents_final = len(posidents)

        # create chunks
        chunks = create_chunks(posidents, self.posidents_per_request)

        # process posident chunks and return xml response as the dict
        dictionary = {}
        dictionary_errors = {}
        for chunk in chunks:
            partial_dictionary = {}
            partial_dictionary_errors = {}
            try:
                vysledek = self.client.service.ctios(pOSIdent=chunk)
                partial_dictionary, partial_dictionary_errors = CtiOSDict()(
                    helpers.serialize_object(vysledek, dict), self.counter, self.logger
                )
            except Exception as exc:
                raise WSDPRequestError(self.logger, exc) from exc

            dictionary = {**dictionary, **partial_dictionary}
            dictionary_errors = {**dictionary_errors, **partial_dictionary_errors}
        return dictionary, dictionary_errors

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
                    self.number_of_posidents_final / self.posidents_per_request
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
                math.ceil(self.number_of_posidents_final / self.posidents_per_request)
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
        :rtype: dict
        """
        try:
            zeep_object = self.client.service.generujCenoveUdajeDleKu(
                katastrUzemiKod=dictionary["katastrUzemiKod"],
                rok=dictionary["rok"],
                mesicOd=dictionary["mesicOd"],
                mesicDo=dictionary["mesicDo"],
                format=dictionary["format"],
            )
            return SestavyDict()(
                helpers.serialize_object(zeep_object, dict), self.logger
            )
        except Exception as exc:
            raise WSDPRequestError(self.logger, exc) from exc


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
        :rtype: dict
        """
        try:
            zeep_object = self.client.service.seznamSestav(idSestavy=id_sestavy)
            return SestavyDict()(
                helpers.serialize_object(zeep_object, dict), self.logger
            )
        except Exception as exc:
            raise WSDPRequestError(self.logger, exc) from exc


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
        :rtype: dict
        """
        try:
            zeep_object = self.client.service.vratSestavu(idSestavy=id_sestavy)
            return SestavyDict()(
                helpers.serialize_object(zeep_object, dict), self.logger
            )
        except Exception as exc:
            raise WSDPRequestError(self.logger, exc) from exc


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
        :rtype: dict
        """
        try:
            zeep_object = self.client.service.smazSestavu(idSestavy=id_sestavy)
            return SestavyDict()(
                helpers.serialize_object(zeep_object, dict), self.logger
            )
        except Exception as exc:
            raise WSDPRequestError(self.logger, exc) from exc
