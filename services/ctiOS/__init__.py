"""
@package ctiOS

@brief Base class creating the interface for ctiOS services

Classes:
 - ctiOS::CtiOSBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os
import math

from services.ctiOS.helpers import CtiOSXMLParser, CtiOSCounter
from services.ctiOS.exceptions import CtiOSInfo
from base import WSDPBase
from base.logger import WSDPLogger

posidents_per_request = 10


class CtiOSBase(WSDPBase):
    """A abstract class that defines interface and main logic used for ctiOS service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.

    Derived class must override get_posidents_from_db(), write_output() methods.
    """
    service_name = "ctiOS"
    logger = WSDPLogger(service_name)

    def __init__(self, username, password):
        super().__init__(username, password)

    def get_default_log_dir(self):
        """Method for getting default log dir"""
        return os.path.join(self.get_service_path(), "logs")

    def get_default_out_dir(self):
        """Method for getting default output dir"""
        return os.path.join(self.get_service_path(), "data", "output")

    def parseXML(self, content):
        """Call ctiOS XML parser"""
        return CtiOSXMLParser()(
            content=content, counter=self.counter, logger=self.logger
        )

    def get_posidents_from_txt(self, txt_path):
        """Get posident array from text file (delimiter is ',')."""
        with open(txt_path) as f:
            ids = f.read().split(",")
        ids_array = []
        for i in ids:
            row = "<v2:pOSIdent>{}</v2:pOSIdent>".format(i)
            ids_array.append(row)
        return ids_array

    def get_posidents_from_db(self):
        """Get posident array from db."""
        raise NotImplementedError(self.__class__.__name__ + "get_posidents_from_db")

    def write_output(self):
        """Abstract method for writing results to output file"""
        raise NotImplementedError(self.__class__.__name__ + "write_output")

    def write_stats(self):
        """Abstract method for for getting service name"""
        CtiOSInfo(
            self.logger,
            "Pocet dotazovanych posidentu: {}.".format(self.number_of_posidents),
        )
        CtiOSInfo(
            self.logger,
            "Pocet pozadavku do ktereho byl dotaz rozdelen: {}.".format(
                self.number_of_chunks
            ),
        )
        CtiOSInfo(
            self.logger,
            "Pocet uspesne stazenych posidentu: {}".format(
                self.counter.uspesne_stazeno
            ),
        )
        CtiOSInfo(
            self.logger,
            "Neplatny identifikator: {}x.".format(self.counter.neplatny_identifikator),
        )
        CtiOSInfo(
            self.logger,
            "Expirovany identifikator: {}x.".format(
                self.counter.expirovany_identifikator
            ),
        )
        CtiOSInfo(
            self.logger,
            "Opravneny subjekt neexistuje: {}x.".format(
                self.counter.opravneny_subjekt_neexistuje
            ),
        )

    def process(self, ids_array):
        """Main wrapping method"""
        self.counter = CtiOSCounter()

        self.number_of_posidents = len(ids_array)
        self.number_of_chunks = math.ceil(len(ids_array) / posidents_per_request)

        def create_chunks(lst, n):
            """"Create n-sized chunks from list as a generator"""
            n = max(1, n)
            return (lst[i : i + n] for i in range(0, len(lst), n))

        ids_chunks = create_chunks(ids_array, posidents_per_request)
        for chunk in ids_chunks:
            xml = self.renderXML(posidents="".join(chunk))
            response_xml = self.call_service(xml)
            dictionary = self.parseXML(response_xml)
            if dictionary:
                self.write_output(dictionary)
        self.write_stats()
