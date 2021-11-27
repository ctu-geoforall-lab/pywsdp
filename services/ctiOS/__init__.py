"""
@package ctiOS

@brief Base class creating the interface for ctiOS services

Classes:
 - ctiOS::CtiOS

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os
import csv
import json
import math
from datetime import datetime

from services.ctiOS.helpers import CtiOSXMLParser, CtiOSCounter
from base import WSDPBase

posidents_per_request = 10


class CtiOSBase(WSDPBase):
    """A class that defines interface and main logic used for ctiOS service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.

    Derived class must override get_posidents_from_db(), write_output() methods.
    """
    service_group = service_name = "ctiOS"

    @property
    def service_name(self):
        """A service name object"""
        pass

    @property
    def xml_attrs(self):
        """XML attributes prepared for XML template rendering"""
        xml_params = []
        posidents = self._get_parameters()

        def create_chunks(lst, n):
            """"Create n-sized chunks from list as a generator"""
            n = max(1, n)
            return (lst[i : i + n] for i in range(0, len(lst), n))

        chunks = create_chunks(posidents, posidents_per_request)
        for chunk in chunks:
            for idx in range(len(chunk)):
                chunk[idx] = "<v2:pOSIdent>{}</v2:pOSIdent>".format(chunk[idx])
            chunk = "".join(chunk)
            xml_params.append(chunk)
        return xml_params

    def _get_parameters(self):
        """Method for getting parameters"""
        pass

    def _set_service_dir(self):
        """Method for getting absolute service path"""
        return os.path.join(self._modules_dir, self.service_group)

    def _parseXML(self, content):
        """Call ctiOS XML parser"""
        return CtiOSXMLParser()(
            content=content, counter=self.counter, logger=self.logger
        )

    def _write_stats(self):
        """Method for getting service stats"""
        self.number_of_posidents = len(self._get_parameters())
        self.number_of_chunks = math.ceil(len(self._get_parameters()) / posidents_per_request)

        self.logger.info(
            "Pocet dotazovanych posidentu: {}".format(self.number_of_posidents)
        )
        self.logger.info(
            "Pocet pozadavku do ktereho byl dotaz rozdelen: {}".format(
                self.number_of_chunks
            )
        )
        self.logger.info(
            "Pocet uspesne stazenych posidentu: {}".format(
                self.counter.uspesne_stazeno
            )
        )
        self.logger.info(
            "Neplatny identifikator: {}x".format(self.counter.neplatny_identifikator),
        )
        self.logger.info(
            "Expirovany identifikator: {}x".format(
                self.counter.expirovany_identifikator
            )
        )
        self.logger.info(
            "Opravneny subjekt neexistuje: {}x".format(
                self.counter.opravneny_subjekt_neexistuje
            )
        )

    def _write_output_to_csv(self, output_dir, result_dict):
        """Write dictionary to csv"""
        date = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
        output_file = "ctios_{}.csv".format(date)
        output = os.path.join(output_dir, output_file)

        header = sorted(set(i for b in map(dict.keys, result_dict.values()) for i in b))
        with open(output, "w", newline="") as f:
            write = csv.writer(f)
            write.writerow(["posident", *header])
            for a, b in result_dict.items():
                write.writerow([a] + [b.get(i, "") for i in header])
            self.logger.info(
                    "Vystupni soubor je k dispozici zde: {}".format(output)
            )
        return output

    def _write_output_to_json(self, output_dir, result_dict):
        """Write dictionary to csv"""
        date = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
        output_file = "ctios_{}.json".format(date)
        output = os.path.join(output_dir, output_file)

        with open(output, "w", newline="", encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False)
            self.logger.info(
                    "Vystupni soubor je k dispozici zde: {}".format(output)
            )
        return output

    def _process(self):
        """Main wrapping method"""
        dictionary = {}
        self.counter = CtiOSCounter()
        for xml_attr in self.xml_attrs:
            xml = self._renderXML(posidents=xml_attr)
            response_xml = self._call_service(xml)
            dictionary = {**dictionary, **self._parseXML(response_xml)}
        self._write_stats()
        return dictionary

