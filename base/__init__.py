"""
@package base

@brief Base abstract class creating the interface for WSDP services

Classes:
 - base::WSDPBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""


import os
import requests
import configparser
from abc import ABC, abstractmethod

from base.exceptions import WSDPRequestError
from base.template import WSDPTemplate



class WSDPBase(ABC):
    """Base abstract class creating the interface for WSDP services"""

    def __init__(self, username, password):
        self._username = username
        self._password = password

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

    @abstractmethod
    def get_service_name(self):
        """Abstract method for for getting service name"""
        raise NotImplementedError

    @abstractmethod
    def get_default_log_dir(self):
        """Abstract method for getting a default service log dir"""
        raise NotImplementedError

    @abstractmethod
    def get_default_out_dir(self):
        """Abstract method for getting a default output dir"""
        raise NotImplementedError

    @property
    @abstractmethod
    def logger(self):
        """A logger object to log messages to"""
        raise NotImplementedError

    def get_config_path(self):
        """
        Method for service headers that must be redefined in subclass
        Returns:
            config_dir (string)
        """
        config_path = os.path.join(os.path.abspath(self.get_service_name()),
                                     'config',
                                     'settings.ini')
        return config_path

    def get_template_path(self):
        """
        Get XML template path needed for rendering XML request
        Returns:
            template path (string):  path for rendered XML request
        """
        template_path = os.path.join(os.path.abspath(self.get_service_name()),
                                     'config',
                                     self._config['files']['xml_template'])
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
        self.service_headers['content_type'] = self._config['service headers']['content_type']
        self.service_headers['accept_encoding'] = self._config['service headers']['accept_encoding']
        self.service_headers['soap_action'] = self._config['service headers']['soap_action']
        self.service_headers['connection'] = self._config['service headers']['connection']
        self.service_headers['endpoint'] = self._config['service headers']['endpoint']

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
        _headers = {"Content-Type": self.service_headers['content_type'],
                    "Accept-Encoding": self.service_headers['accept_encoding'],
                    "SOAPAction": self.service_headers['soap_action'],
                    "Connection": self.service_headers['connection']}
        try:
            response_xml = requests.post(self.service_headers['endpoint'],
                                         data=xml,
                                         headers=_headers).text
            #if self.log_dir:
            #    self.logger.debug(response_xml)
        except requests.exceptions.RequestException as e:
            raise WSDPRequestError(self.logger, e)
        return response_xml

    def renderXML(self, **kwargs):
        """Abstract method rendering XML"""
        request_xml = WSDPTemplate(self.template_path).render(username=self._username, password=self._password, **kwargs)
        return request_xml

    @abstractmethod
    def parseXML(self):
        """Abstract method for parsing XML"""
        raise NotImplementedError






