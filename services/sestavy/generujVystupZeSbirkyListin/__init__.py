"""
@package pywsdp

@brief Base class creating the interface for generujVystupZeSbirkyListin service

Classes:
 - generujVystupZeSbirkyListin::GenerujVystupZeSbirkyListin

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

from base import WSDPBase
from base.logger import WSDPLogger


class GenerujVystupZeSbirkyListin(WSDPBase):
    """A concrete class that defines interface and main logic
    used for generujVystupZeSbirkyListin service.
    """

    service_type = "sestavy"
    service_name = "generujVystupZeSbirkyListin"
    logger = WSDPLogger(service_name)

    def __init__(self, username, password, csv_path):
        super().__init__(username, password)
        self.csv_path = csv_path

    def parseXML(self, content):
        """Call ctiOS XML parser"""
        #return GenerujListinuXMLParser()(
        #    content=content, logger=self.logger
        #)
        return 1

    def get_parameters_from_txt(self, txt_path):
        """Get parameters array from text file (delimiter is ',')."""
        parameters_array = []
        with open(txt_path) as f:
            for line in f:
                key, value = line.split()
                row = "<v2:{0}>{1}</v2:{0}>".format(key, value)
                parameters_array.append(row)
        return parameters_array

    def process(self, parameters_array):
        """Main wrapping method"""
        xml = self.renderXML(parameters="".join(parameters_array))
        print(xml)
        response_xml = self.call_service(xml)
        print(response_xml)