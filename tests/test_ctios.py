import sys
import os
import pytest
import configparser
from pathlib import Path
from shutil import copyfile

sys.path.insert(0, str(Path(__file__).parent))
from pywsdp.modules import CtiOS


class TestCtiOS:

    service_group = service_name = "ctiOS"
    library_path = os.path.abspath('../')
    if library_path not in sys.path:
       sys.path.append(library_path)
    service_dir = os.path.abspath(os.path.join(library_path, 'pywsdp', 'services', 'ctiOS'))

    def test_request_XML(self):
        """Test if created XML from template is not empty and is valid, tag exists."""
        ctiOS = CtiOS()
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka"]
        }
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        xml = self.ctiOS.ctios._renderXML(posidents=self.ctiOS.ctios.xml_attr)
        xsd_url = "https://katastr.cuzk.cz/dokumentace/ws28/ctios/ctios_v28.xsd"
        validate = self.ctiOS.ctios._validateXMLByXSD(xml, xsd_url)  
        assert validate == True

    def test_response_XML(self):
        """Send XML, check http error code, check response XML (not empty, is valid, check nonvalid posidents)"""
        ctiOS = CtiOS()
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka"]
        }
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        xml = self.ctiOS.ctios._renderXML(posidents=self.ctiOS.ctios.xml_attr)
        response_xml = self.ctiOS.ctios._call_service(xml)
        xsd_url = "https://katastr.cuzk.cz/dokumentace/ws28/ctios/ctios_v28.xsd"
        validate = self.ctiOS.ctios._validateXMLByXSD(response_xml, xsd_url)  
        assert validate == True
