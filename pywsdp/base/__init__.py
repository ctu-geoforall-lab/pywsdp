"""
@package base

@brief Base abstract class creating the interface for WSDP services

Classes:
 - base::WSDPBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os
import requests
import configparser
from abc import ABC, abstractmethod

from pywsdp.base.exceptions import WSDPRequestError
from pywsdp.base.template import WSDPTemplate

__version__ = '1.0'


class WSDPBase(ABC):
    """Base abstract class creating the interface for WSDP services
    Several methods has to be overridden.
    """

    def __init__(self):
        self._username = None
        self._password = None
        self._request_xml = None
        self._response_xml = None
        self._services_dir = self._find_services_dir()
        self._service_dir = self._set_service_dir()
        self._config = self._read_configuration()
        self._service_headers = self._set_service_headers()
        self._set_template_path()

    @property
    @abstractmethod
    def service_group(self):
        """A type group services - ctiOS, sestavy, vyhledat, ciselniky etc."""
        pass

    @property
    @abstractmethod
    def service_name(self):
        """A service name object"""
        pass

    @property
    @abstractmethod
    def xml_attrs(self):
        """XML attributes prepared for XML template rendering"""
        pass

    @classmethod
    def _from_recipe(cls, args, logger):
        """Creates class instance based on the recipe"""
        result = cls()
        result.args = args
        result.logger = logger
        return result

    @property
    def username(self):
        """User can get usernamer"""
        return self._username

    @property
    def password(self):
        """User can get password"""
        return self._password

    def set_credentials(self, username, password):
        """User can set credentials"""
        self._username = username
        self._password = password

    @property
    def services_dir(self):
        """User can get services dir"""
        return self._services_dir

    def _find_services_dir(self):
        """"Get modules path according to the way the library is run"""

        def is_run_by_jupyter():
            import __main__ as main
            return not hasattr(main, '__file__')

        if is_run_by_jupyter():
            return os.path.abspath(os.path.join('../../../', 'pywsdp', 'services'))
        else:
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services')

    @property
    def service_dir(self):
        """User can get log dir"""
        return self._service_dir

    @abstractmethod
    def _set_service_dir(self):
        """Method for getting absolute service path"""
        pass

    @property
    def config_path(self):
        """User can get config path"""
        return self._config_path

    def _read_configuration(self):
        """
        Set config path needed for getting headers for given service
        Returns:
            config_dir (string)
        """
        self._config_path = os.path.join(
            self.service_dir, "config", "settings.ini"
        )
        config = configparser.ConfigParser()
        config.read(self._config_path)
        return config

    @property
    def template_path(self):
        """User can get template path"""
        return self._template_path

    def _set_template_path(self, template_path=None):
        """
        Set XML template path needed for rendering XML request
        Returns:
            template path (string):  path for rendered XML request (optional)
            If template path is not set, the default one is selected.
        """
        if not template_path:
            self._template_path = os.path.join(
                self.service_dir,
                "config",
                self._config["files"]["xml_template"],
            )
        else:
            self._template_path = template_path

    @property
    def service_headers(self):
        """User can get service headers"""
        return self._service_headers

    def _set_service_headers(self):
        """
        Set service headers needed for calling WSDP service
        Returns:
            service headers (dictionary):  parameters for calling WSDP service
        """
        # CTIOS service parameters loaded from ini file
        service_headers = {}
        service_headers["content_type"] = self._config["service headers"][
            "content_type"
        ]
        service_headers["accept_encoding"] = self._config["service headers"][
            "accept_encoding"
        ]
        service_headers["soap_action"] = self._config["service headers"][
            "soap_action"
        ]
        service_headers["connection"] = self._config["service headers"][
            "connection"
        ]
        service_headers["endpoint"] = self._config["service headers"]["endpoint"]
        return service_headers

    def _renderXML(self, **kwargs):
        """Abstract method rendering XML"""
        request_xml = WSDPTemplate(self.template_path).render(
            username=self._username, password=self._password, **kwargs
        )
        return request_xml

    def _call_service(self, xml):
        """Send a request in the XML form to WSDP service
        Args:
            request_xml (str): xml for requesting WSDP service
        Raises:
            WSDPRequestError(Service error)
        Returns:
            response from WSDP service
        """
        # WSDP headers for service requesting
        _headers = {
            "Content-Type": self.service_headers["content_type"],
            "Accept-Encoding": self.service_headers["accept_encoding"],
            "SOAPAction": self.service_headers["soap_action"],
            "Connection": self.service_headers["connection"],
        }
        try:
            r = requests.post(
                self.service_headers["endpoint"], data=xml, headers=_headers
            )
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            raise WSDPRequestError(self.logger, e)
        return None

    @abstractmethod
    def _parseXML(self, content):
        """Call XML parser"""
        pass

    def _process(self):
        """Main wrapping method"""
        dictionary = {}
        if isinstance(self.xml_attrs, list):
            for xml_attr in self.xml_attrs:
                request_xml = self._renderXML(parameters=xml_attr)
                response_xml = self._call_service(request_xml).text
                dictionary = {**dictionary, **self._parseXML(response_xml)}
        else:
            request_xml = self._renderXML(parameters=self.xml_attrs)
            response_xml = self._call_service(request_xml).text
            dictionary = self._parseXML(response_xml)
        self.request_xml = request_xml
        self.response_xml = response_xml
        return dictionary

    def _test_service(self):
        """Test service"""
        if isinstance(self.xml_attrs, list):
            xml = self._renderXML(parameters=self.xml_attrs[0])
        else:
            xml = self._renderXML(parameters=self.xml_attrs)
        return self._call_service(xml).status_code
