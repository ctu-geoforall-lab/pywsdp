###############################################################################
# Name:         abstract class WSDP_base
# Purpose:      Creates the interface for WSDP services.
# Date:         March 2021
# Copyright:    (C) 2021 Linda Kladivova
# Email:        l.kladivova@seznam.cz
###############################################################################

import abc
import requests

from wsdp.logger import Logger
from wsdp.exceptions import WSDPRequestError


class WSDPbase():
    """Abstract class to connect to service and to return XML."""
    __metaclass__ = abc.ABCMeta # Declares class as abstract

    def __init__(self, user, password, log_dir=None):
        self.user = user
        self.password = password

        if log_dir:
            name = self.define_log_name()
            self.logger = Logger(name=name)
            self.logger.set_directory(log_dir)
            self.log_dir = log_dir

        self.service_headers = self.define_service_headers()
        self.xml = self.draw_up_xml_request()
        self.attributes = self.create_parser()
        self.create_output()

    @abc.abstractmethod
    def define_log_name(self):
        """Abstract method for defining logger name according to service - must be redefined in subclass"""
        pass

    @abc.abstractmethod
    def define_service_headers(self):
        """
        Abstract method for service headers that must be redefined in subclass
        Returns:
            service headers (dictionary): parameters for calling a service
        """
        pass

    @abc.abstractmethod
    def draw_up_xml_request(self):
        """
        Abstract method for drawing xml service up - must be redefined in subclass
        Returns:
            request_xml (str): xml request for a service
        """
        pass

    def call_service(self):
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
                                         data=self.xml,
                                         headers=_headers).text
            if self.log_dir:
                Logger.debug(response_xml)
        except requests.exceptions.RequestException as e:
            raise WSDPRequestError(e)
        return response_xml

    @abc.abstractmethod
    def create_parser(self):
        """
        Abstract method for defining class for drawing xml service up - must be redefined in subclass
        Returns:
            attributes (dictionary): all processed attributes 
        """
        pass

    @abc.abstractmethod
    def create_output(self):
        """Abstract method for creating the final output - must be redefined in subclass"""
        pass






