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

from base.exceptions import WSDPRequestError
from base.template import WSDPTemplate


class WSDPBase(ABC):
    """Base abstract class creating the interface for WSDP services

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.

    Derived class must override logger(), service_name(),
    get_parameters_from_txt(), parse_xml() methods.
    """

    def __init__(self):
        self._username = "WSTEST"
        self._password = "WSHESLO"
        self._modules_dir = self._find_module_dir()
        self._service_dir = self._set_service_dir()
        self._log_dir = self._set_default_log_dir()
        self._config = self._read_configuration()
        self._template_path = self._set_template_path()
        self._service_headers = self._set_service_headers()
        self._result_dict = None

    @property
    @abstractmethod
    def logger(self):
        """A logger object to log messages to"""
        pass

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

    @classmethod
    def _from_recipe(cls, parameters):
        result = cls()
        result.parameters = parameters
        return result

    def __repr__(self):
        return f"{self.service_group}->{ self.service_name}"

    @property
    def xml_attrs(self):
        xml_params = []
        for key, value in self.parameters.items():
             row = "<v2:{0}>{1}</v2:{0}>".format(key, value)
             xml_params.append(row)
        return "".join(xml_params)

    @property
    def username(self):
        """User can get usernamer"""
        return self._username

    @property
    def password(self):
        """User can get password"""
        return self._password

    @username.setter
    def username(self, username):
        """User can get usernamer"""
        self._username = username

    @password.setter
    def password(self, password):
        """User can get password"""
        self._password = password

    @property
    def credentials(self):
        """User can get log dir"""
        return (self._username, self._password)

    @property
    def modules_dir(self):
        """User can get module dir"""
        return self._modules_dir

    def _find_module_dir(self):
        """"Get modules path according to the way the library is run"""

        def is_run_by_jupyter():
            import __main__ as main
            return not hasattr(main, '__file__')

        if is_run_by_jupyter():
            return os.path.abspath(os.path.join('../../', 'services'))
        else:
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services')

    @property
    def service_dir(self):
        """User can get log dir"""
        return self._service_dir

    def _set_service_dir(self):
        """Method for getting absolute service path"""
        return os.path.join(self._modules_dir, self.service_group, self.service_name)

    @property
    def log_dir(self):
        """User can get log dir"""
        return self._log_dir

    @log_dir.setter
    def log_dir(self, log_dir):
        """User can set log dir"""
        self._ensure_dir_exists(log_dir)
        self.logger.set_directory(log_dir)
        self._log_dir = log_dir

    def _set_default_log_dir(self):
        """Method for getting default log dir"""
        log_dir = os.path.join(self.service_dir, "logs")
        self._ensure_dir_exists(log_dir)
        self.logger.set_directory(log_dir)
        return log_dir

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

    def _set_template_path(self):
        """
        Set XML template path needed for rendering XML request
        Returns:
            template path (string):  path for rendered XML request
        """
        template_path = os.path.join(
            self.service_dir,
            "config",
            self._config["files"]["xml_template"],
        )
        return template_path

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

    def _ensure_dir_exists(self, directory):
        """Method for checking if dir exists.
        If does not exist, it creates a new dir"""
        if not os.path.exists(directory):
            os.makedirs(directory)

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
            response_xml (str): xml response from WSDP service
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
            # if self.log_dir:
            #    self.logger.debug(response_xml)
        except requests.exceptions.RequestException as e:
            raise WSDPRequestError(self.logger, e)
        response_xml = r.text
        return response_xml

    @abstractmethod
    def _parseXML(self, content):
        """Call XML parser"""
        pass

    def process(self):
        """Main wrapping method"""
        xml = self._renderXML(parameters=self.xml_attrs)
        response_xml = self._call_service(xml)
        self.result_dict = self._parseXML(response_xml)