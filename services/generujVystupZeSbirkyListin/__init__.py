"""
@package pywsdp

@brief Base class creating the interface for generujVystupZeSbirkyListin service

Classes:
 - generujVystupZeSbirkyListinBase::GenerujVystupZeSbirkyListinBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

from base import WSDPBase


class GenerujVystupZeSbirkyListinBase(WSDPBase):
    """A abstract class that defines interface and main logic used for generujVystupZeSbirkyListin service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    def __init__(self, username, password):
        raise NotImplementedError