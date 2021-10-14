"""
@package pywsdp

@brief Base class creating the interface for generujCenoveUdajeDleKu service

Classes:
 - generujCenoveUdajeDleKuBase::GenerujCenoveUdajeDleKuBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

from base import WSDPBase


class GenerujCenoveUdajeDleKuBase(WSDPBase):
    """A abstract class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    def __init__(self, username, password):
        raise NotImplementedError
