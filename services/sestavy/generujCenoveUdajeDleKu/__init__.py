"""
@package pywsdp

@brief Base class creating the interface for generujCenoveUdajeDleKu service

Classes:
 - generujCenoveUdajeDleKuBase::GenerujCenoveUdajeDleKuBase

Classes:
 - generujCenoveUdajeDleKu::GenerujCenoveUdajeDleKu

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os
from datetime import datetime

from services.sestavy import SestavyBase
from base.logger import WSDPLogger


class GenerujCenoveUdajeDleKu(SestavyBase):
    """A class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    service_name = "generujCenoveUdajeDleKu"
    logger = WSDPLogger(service_name)

    def __init__(self, username, password):
        super().__init__(username, password)

    def get_service_path(self):
        """Method for getting absolute service path"""
        return os.path.join(self.modules_dir, self.service_group, self.service_name)

    def process(self):
        """Main wrapping method"""
        xml = self.renderXML(parameters="".join(self.parameters))
        response_xml = self.call_service(xml)
        self.xml_dict = self.parseXML(response_xml)

    def get_parameters_from_file(self, txt_path):
        """Get parameters list from text file (delimiter is ',')."""
        self.parameters = []
        with open(txt_path) as f:
            for line in f:
                key, value = line.split()
                row = "<v2:{0}>{1}</v2:{0}>".format(key, value)
                self.parameters.append(row)

    def write_output(self, output_dir=None):
        """Decode base64 string and write output to out dir"""
        import base64
        binary = base64.b64decode(self.get_soubor_sestavy())
        if not output_dir:
            output_dir = self.get_default_out_dir()
        date = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
        output_file = "cen_udaje_{}.{}".format(date, self.get_format())
        with open(os.path.join(output_dir, output_file), 'wb') as f:
            f.write(binary)
