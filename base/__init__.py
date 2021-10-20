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

    Derived class must override get_service_name(), get_default_log_dir(),
    get_default_out_dir(), logger(), parse_xml() methods.
    """

    def __init__(self, username, password):
        self._username = username
        self._password = password

        # Set modules directory
        self.modules_dir = self.get_module_path()

        # Set default output dir
        self.out_dir = self.get_default_out_dir()

        # Set default log dir and
        log_dir = self.get_default_log_dir()
        self.logger.set_directory(log_dir)

        # Read configuration from config file
        config_path = self.get_config_path()
        self._config = configparser.ConfigParser()
        self._config.read(config_path)

        # Set headers
        self.get_service_headers()
        self.template_path = self.get_template_path()

    @property
    def logger(self):
        """A logger object to log messages to"""
        raise NotImplementedError

    @property
    def service_name(self):
        """A service name object"""
        raise NotImplementedError

    def is_run_by_jupyter(self):
        import __main__ as main
        return not hasattr(main, '__file__')

    def get_module_path(self):
        if self.is_run_by_jupyter():
            return os.path.abspath(os.path.join('../../', 'services'))
        else:
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services')

    def get_service_path(self):
        """Method for getting absolute service path"""
        return os.path.join(self.modules_dir, self.service_name)

    def get_default_log_dir(self):
        """Method for getting default log dir"""
        return os.path.join(self.get_service_path(), "logs")

    def get_default_out_dir(self):
        """Method for getting default output dir"""
        return os.path.join(self.get_service_path(), "data", "output")

    def get_config_path(self):
        """
        Get config path needed for getting headers for given service
        Returns:
            config_dir (string)
        """
        config_path = os.path.join(
            self.get_service_path(), "config", "settings.ini"
        )
        return config_path

    def get_template_path(self):
        """
        Get XML template path needed for rendering XML request
        Returns:
            template path (string):  path for rendered XML request
        """
        template_path = os.path.join(
            self.get_service_path(),
            "config",
            self._config["files"]["xml_template"],
        )
        return template_path

    def set_log_dir(self, log_dir):
        """User can set log dir"""
        self.log_dir = log_dir
        self.logger.set_directory(log_dir)

    def set_out_dir(self, out_dir):
        """User can set output dir"""
        self.out_dir = out_dir

    def get_log_dir(self):
        """User can get log dir"""
        return self.log_dir

    def get_out_dir(self):
        """User can get output dir"""
        return self.out_dir

    def get_service_headers(self):
        """
        Get service headers needed for calling WSDP service
        Returns:
            service headers (dictionary):  parameters for calling WSDP service
        """
        # CTIOS service parameters loaded from ini file
        self.service_headers = {}
        self.service_headers["content_type"] = self._config["service headers"][
            "content_type"
        ]
        self.service_headers["accept_encoding"] = self._config["service headers"][
            "accept_encoding"
        ]
        self.service_headers["soap_action"] = self._config["service headers"][
            "soap_action"
        ]
        self.service_headers["connection"] = self._config["service headers"][
            "connection"
        ]
        self.service_headers["endpoint"] = self._config["service headers"]["endpoint"]

    def call_service(self, xml):
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
            response_xml = requests.post(
                self.service_headers["endpoint"], data=xml, headers=_headers
            ).text
            # if self.log_dir:
            #    self.logger.debug(response_xml)
        except requests.exceptions.RequestException as e:
            raise WSDPRequestError(self.logger, e)
        return response_xml

    def renderXML(self, **kwargs):
        """Abstract method rendering XML"""
        request_xml = WSDPTemplate(self.template_path).render(
            username=self._username, password=self._password, **kwargs
        )
        return request_xml

    @abstractmethod
    def get_parameters_from_txt(self):
        """Abstract method for getting request parameters from txt"""
        raise NotImplementedError(self.__class__.__name__ + "get_parameters_from_txt")

    @abstractmethod
    def parseXML(self):
        """Abstract method for parsing XML"""
        raise NotImplementedError(self.__class__.__name__ + "parseXML")
