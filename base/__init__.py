"""
@package base

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
from base.template import WSDPTemplate



class WSDPBase(object):
    """Base abstract class creating the interface for WSDP services"""
    __metaclass__ = abc.ABCMeta # Declares class as abstract

    def __init__(self, username, password, config_path=None, out_dir=None, log_dir=None):
        self._username = username
        self._password = password

        # Get user-defined or default output dir
        if not out_dir:
            out_dir = self.get_default_out_dir()
        self.out_dir = out_dir

        # Get user-defined or default log dir
        if not log_dir:
            log_dir = self.get_default_log_dir()
        self.log_dir = log_dir

        if not config_path:
            config_path = self.get_config_path()

        # Read configuration from config file
        self._config = configparser.ConfigParser()
        self._config.read(config_path)

        # Set headers
        self.get_service_headers()
        self.template_path = self.get_template_path()

    @abc.abstractmethod
    def get_service_name(self):
        """Abstract method for for getting service name"""
        pass

    @abc.abstractmethod
    def get_default_log_dir(self):
        """Abstract method for getting a default service log dir"""
        pass

    @abc.abstractmethod
    def get_default_out_dir(self):
        """Abstract method for getting a default output dir"""
        pass

    @property
    @abc.abstractmethod
    def logger(self):
        """A logger object to log messages to - must be redefined in subclass"""
        pass

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
                                     self._config['files']['request_xml_file'])
        return template_path

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

    @abc.abstractmethod
    def parseXML(self):
        """Abstract method for parsing XML"""
        pass






