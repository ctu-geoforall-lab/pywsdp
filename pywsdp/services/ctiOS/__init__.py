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

from pywsdp.base import WSDPBase
from pywsdp.services.ctiOS.helpers import CtiOSXMLParser, CtiOSCounter

posidents_per_request = 10


class CtiOSBase(WSDPBase):
    """A class that defines interface and main logic used for ctiOS service.
    Derived class must override service_name property and _get_parameters() method.
    """

    def __init__(self):
        super().__init__()
        self.counter = CtiOSCounter()

    @property
    def service_name(self):
        """A service name object"""
        pass

    @property
    def service_group(self):
        """A service group object"""
        return "ctiOS"

    @property
    def parameters(self):
        """Method for getting parameters"""
        pass

    @property
    def number_of_posidents(self):
        return len(self.parameters)

    @property
    def number_of_posidents_final(self):
        return len(list(dict.fromkeys(self.parameters)))

    @property
    def number_of_chunks(self):
        return math.ceil(self.number_of_posidents_final / posidents_per_request)

    @property
    def xml_attrs(self):
        """XML attributes prepared for XML template rendering"""

        def create_chunks(lst, n):
            """"Create n-sized chunks from list as a generator"""
            n = max(1, n)
            return (lst[i : i + n] for i in range(0, len(lst), n))

        xml_params = []
        self.posidents = list(dict.fromkeys(self.parameters)) # remove duplicates
        chunks = create_chunks(self.posidents, posidents_per_request)
        for chunk in chunks:
            for idx in range(len(chunk)):
                chunk[idx] = "<v2:pOSIdent>{}</v2:pOSIdent>".format(chunk[idx])
            chunk = "".join(chunk)
            xml_params.append(chunk)
        return xml_params

    def _set_service_dir(self):
        """Method for getting absolute service path"""
        return os.path.join(self._services_dir, self.service_group)

    def _parseXML(self, content):
        """Call ctiOS XML parser"""
        return CtiOSXMLParser()(
            content=content, counter=self.counter, logger=self.logger
        )

    def write_preprocessing_stats(self):
        """Method for getting preprocessing stats"""
        self.logger.info(
            "Pocet dotazovanych posidentu: {}".format(self.number_of_posidents)
        )
        self.logger.info(
            "Pocet zjistenych duplicitnich identifikatoru: {}".format(
                self.number_of_posidents - self.number_of_posidents_final
            )
        )
        self.logger.info(
            "Realny pocet identifikatoru po odstraneni duplicit: {}".format(
                self.number_of_posidents_final
            )
        )
        self.logger.info(
            "Pocet pozadavku do kterych bude dotaz rozdelen: {}".format(
                self.number_of_chunks
            )
        )

    def _write_output_to_csv(self, result_dict, output_csv):
        """Write dictionary to csv"""
        header = sorted(set(i for b in map(dict.keys, result_dict.values()) for i in b))
        with open(output_csv, "w", newline="") as f:
            write = csv.writer(f)
            write.writerow(["posident", *header])
            for a, b in result_dict.items():
                write.writerow([a] + [b.get(i, "") for i in header])
            self.logger.info(
                    "Vystup byl ulozen zde: {}".format(output_csv)
            )

    def _write_output_to_json(self, result_dict, output_json):
        """Write dictionary to json"""
        with open(output_json, "w", newline="", encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False)
            self.logger.info(
                    "Vystup byl ulozen zde: {}".format(output_json)
            )

    def write_postprocessing_stats(self):
        self.logger.info(
            "Pocet uspesne stazenych posidentu: {}".format(
                self.counter.uspesne_stazeno
            )
        )
        self.logger.info(
            "Pocet neplatnych identifikatoru: {}".format(self.counter.neplatny_identifikator),
        )
        self.logger.info(
            "Pocet expirovanych identifikatoru: {}".format(
                self.counter.expirovany_identifikator
            )
        )
        self.logger.info(
            "Pocet identifikatoru neexistujicich opravnenych subjektu: {}".format(
                self.counter.opravneny_subjekt_neexistuje
            )
        )

    def _process(self):
        """Main wrapping method"""
        dictionary = super()._process()
        self.write_postprocessing_stats()
        return dictionary
