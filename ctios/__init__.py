"""
@package ctios

@brief Base class creating the interface for CTIOS services

Classes:
 - ctios::CtiOsWSDP
 - ctios::CtiOsBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""

import os
from abc import abstractmethod
import math

from ctios.helpers import CtiOsXMLParser
from ctios.helpers import counter
from ctios.exceptions import CtiOsInfo
from base import WSDPBase
from base.logger import WSDPLogger


logger = ctios_logger = WSDPLogger("pyctios")
posidents_per_request = 10


class CtiOsWSDP(WSDPBase):
    """A concrete creator that implements concrete WSDP atributes for CtiOs class"""

    logger = ctios_logger

    def get_service_name(self):
        """Method for getting service name"""
        return "ctios"

    def get_default_log_dir(self):
        """Method for getting default log dir"""
        return os.path.join(os.path.abspath('logs'), 'ctios')

    def get_default_out_dir(self):
        """Method for getting default output dir"""
        return os.path.join(os.path.abspath('tests'), 'output_data')

    def parseXML(self, content):
        """Call CtiOs XML parser"""
        return CtiOsXMLParser()(content=content,
                                counter=counter,
                                logger=self.logger)


class CtiOsBase(CtiOsWSDP):
    """A abstract class that defines interface and main logic used for CtiOs service."""

    def __init__(self, username, password, config_path=None, out_dir=None, log_dir=None):
        super().__init__(username, password, config_path=None, out_dir=None, log_dir=None)

    @abstractmethod
    def get_input(self):
        """Abstract method for for getting service name"""
        raise NotImplementedError

    @abstractmethod
    def create_output(self):
        """Abstract method for creating output file"""
        raise NotImplementedError

    @abstractmethod
    def write_output(self):
        """Abstract method for writing results to output file"""
        raise NotImplementedError

    def process_input(self, ids_array):
        xml = self.renderXML(posidents=''.join(ids_array))
        response_xml = self.call_service(xml)
        dictionary = self.parseXML(response_xml)
        return dictionary

    def write_stats(self):
        """Abstract method for for getting service name"""
        CtiOsInfo(self.logger, 'Pocet dotazovanych posidentu: {}.'.format(self.number_of_posidents))
        CtiOsInfo(self.logger, 'Pocet pozadavku do ktereho byl dotaz rozdelen: {}.'.format(self.number_of_chunks))
        CtiOsInfo(self.logger, 'Pocet uspesne stazenych posidentu: {}'.format(counter.uspesne_stazeno))
        CtiOsInfo(self.logger, 'Neplatny identifikator: {}x.'.format(counter.neplatny_identifikator))
        CtiOsInfo(self.logger, 'Expirovany identifikator: {}x.'.format(counter.expirovany_identifikator))
        CtiOsInfo(self.logger, 'Opravneny subjekt neexistuje: {}x.'.format(counter.opravneny_subjekt_neexistuje))

    def process(self):
        """Main wrapping method"""
        ids_array = self.get_input()
        self.create_output()
        self.number_of_posidents = len(ids_array)
        self.number_of_chunks = math.ceil(len(ids_array)/posidents_per_request)

        def create_chunks(lst, n):
            """"Create n-sized chunks from list as a generator"""
            n = max(1, n)
            return (lst[i:i+n] for i in range(0, len(lst), n))

        ids_chunks = create_chunks(ids_array, posidents_per_request)
        for chunk in ids_chunks:
            dictionary = self.process_input(chunk)
            if dictionary:
                self.write_output(dictionary)
        self.write_stats()









