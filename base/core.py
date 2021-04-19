"""
@package pywsdp.base

@brief Base abstract class creating the interface for WSDP services

Classes:
 - base::WSDPBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""


import os
import abc
import requests
import configparser

from base.exceptions import WSDPRequestError
from base.logger import WSDPLogger


class WSDPBase(object):
    """Base abstract class creating the interface for WSDP services"""
    __metaclass__ = abc.ABCMeta # Declares class as abstract

    def __init__(self, user, password, log_dir=None, config_dir=None):
        self.user = user
        self.password = password

        if config_dir:
            config_dir = self.get_config_dir()

        if log_dir:
            name = self.define_log_name()
            self.logger = WSDPLogger(name=name)
            self.logger.set_directory(log_dir)
            self.log_dir = log_dir

        # Read configuration from config file
        self._config = configparser.ConfigParser()
        self._config.read(config_dir)

        self.service_headers = self.get_service_headers()
        self.template_dir = self.get_template_dir()

    @abc.abstractmethod
    def define_service_name(self):
        """Abstract method for defining service name - must be redefined in subclass"""
        pass

    @abc.abstractmethod
    def define_log_name(self):
        """Abstract method for defining logger name according to service - must be redefined in subclass"""
        pass

    @abc.abstractmethod
    def get_config_file(self):
        """
        Abstract method for service headers that must be redefined in subclass
        Returns:
            service headers (dictionary): parameters for calling a service:
                content_type, accept_encoding, soap_action, connection, endpoint
        """
        config_dir = os.path.join(os.path.abspath(self.define_service_name()), 'settings.ini')
        return config_dir

    def get_service_headers(self):
        """
        Get service headers needed for calling WSDP service
        Returns:
            service headers (dictionary):  parameters for calling WSDP service
        """
        # CTIOS service parameters loaded from ini file
        service_headers = {}
        service_headers['content_type'] = self._config['service headers']['content_type']
        service_headers['accept_encoding'] = self._config['service headers']['accept_encoding']
        service_headers['soap_action'] = self._config['service headers']['soap_action']
        service_headers['connection'] = self._config['service headers']['connection']
        service_headers['endpoint'] = self._config['service headers']['endpoint']
        return service_headers

    def get_template_dir(self):
        """
        Get XML template dir needed for rendering XML request
        Returns:
            template dir (string):  parameter for rendering XML request
        """
        return self._config['files'].get('template_dir')

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
            if self.log_dir:
                self.logger.debug(response_xml)
        except requests.exceptions.RequestException as e:
            raise WSDPRequestError(e)
        return response_xml

    @abc.abstractmethod
    def renderXML(self):
        """
        Abstract method rendering XML must be redefined in subclass
        """
        pass

    @abc.abstractmethod
    def parseXML(self):
        """
        Abstract method for service headers that must be redefined in subclass
        """
        pass

    @abc.abstractmethod
    def getXMLresponse(self):
        """
        Abstract method for rendering, getting and parsing XML - must be redefined in subclass
        """
        pass






