"""
@package pywsdp

@brief Base class creating the interface for Sestavy service

Classes:
 - base::SestavyBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os

from base import WSDPBase
from services.sestavy.helpers import SestavyXMLParser


class SestavyBase(WSDPBase):
    """An abstract class that defines interface and main logic
    used for other Sestavy services.
    """
    service_group = "sestavy"

    @property
    def service_name(self):
        """A service name object"""
        pass

    @property
    def xml_attrs(self):
        """XML attributes prepared for XML template rendering"""
        xml_params = []
        for key, value in self.parameters.items():
             row = "<v2:{0}>{1}</v2:{0}>".format(key, value)
             xml_params.append(row)
        return "".join(xml_params)

    def _set_service_dir(self):
        """Method for getting absolute service path"""
        return os.path.join(self._modules_dir, self.service_group, self.service_name)

    def _parseXML(self, content):
        """Call sestavy XML parser"""
        return SestavyXMLParser()(
            content=content, logger=self.logger
        )

    def _write_output(self, output_file, base64_string):
        """Decode base64 string and write output to out dir"""
        import base64
        binary = base64.b64decode(base64_string)
        with open(output_file, 'wb') as f:
            f.write(binary)
            self.logger.info(
                    "Vystupni soubor je k dispozici zde: {}".format(output_file)
            )