"""
@package ctios

@brief Base class creating the interface for CTIOS services

Classes:
 - ctios::CtiOsBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""

import os
import math

from ctios.helpers import CtiOsXMLParser, CtiOsCounter
from ctios.exceptions import CtiOsInfo
from base import WSDPBase
from base.logger import WSDPLogger


logger = ctios_logger = WSDPLogger("pyctios")
posidents_per_request = 10


class CtiOsBase(WSDPBase):
    """A abstract class that defines interface and main logic used for CtiOs service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.

    Derived class must override get_posidents_from_db(), write_output() methods.
    """
    logger = ctios_logger

    def __init__(self, username, password):
        super().__init__(username, password)

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
                                counter=self.counter,
                                logger=self.logger)

    def get_posidents_from_txt(self, txt_path):
        """Get posident array from text file (delimiter is ',')."""
        with open(txt_path) as f:
            ids = f.read().split(',')
        ids_array = []
        for i in ids:
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i)
            ids_array.append(row)
        return ids_array

    def get_posidents_from_db(self):
        """Get posident array from db."""
        raise NotImplementedError(self.__class__.__name__+ "get_posidents_from_db")

    def write_output(self):
        """Abstract method for writing results to output file"""
        raise NotImplementedError(self.__class__.__name__+ "write_output")

    def write_stats(self):
        """Abstract method for for getting service name"""
        CtiOsInfo(self.logger, 'Pocet dotazovanych posidentu: {}.'.format(self.number_of_posidents))
        CtiOsInfo(self.logger, 'Pocet pozadavku do ktereho byl dotaz rozdelen: {}.'.format(self.number_of_chunks))
        CtiOsInfo(self.logger, 'Pocet uspesne stazenych posidentu: {}'.format(self.counter.uspesne_stazeno))
        CtiOsInfo(self.logger, 'Neplatny identifikator: {}x.'.format(self.counter.neplatny_identifikator))
        CtiOsInfo(self.logger, 'Expirovany identifikator: {}x.'.format(self.counter.expirovany_identifikator))
        CtiOsInfo(self.logger, 'Opravneny subjekt neexistuje: {}x.'.format(self.counter.opravneny_subjekt_neexistuje))

    def process(self, ids_array):
        """Main wrapping method"""
        self.counter = CtiOsCounter()

        self.number_of_posidents = len(ids_array)
        self.number_of_chunks = math.ceil(len(ids_array)/posidents_per_request)

        def create_chunks(lst, n):
            """"Create n-sized chunks from list as a generator"""
            n = max(1, n)
            return (lst[i:i+n] for i in range(0, len(lst), n))

        ids_chunks = create_chunks(ids_array, posidents_per_request)
        for chunk in ids_chunks:
            xml = self.renderXML(posidents=''.join(chunk))
            response_xml = self.call_service(xml)
            dictionary = self.parseXML(response_xml)
            if dictionary:
                self.write_output(dictionary)
        self.write_stats()

