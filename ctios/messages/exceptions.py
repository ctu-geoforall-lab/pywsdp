###############################################################################
# Name:         CtiOSParser
# Purpose:      Main exception class
# Date:         March 2021
# Copyright:    (C) 2021 Linda Kladivova
# Email:        l.kladivova@seznam.cz
###############################################################################

from wsdp.logger import Logger


class CtiOsError(Exception):
    """General exception for CtiOs errors"""
    def __init__(self, msg):
        Logger.fatal(msg)

class CtiOsInfo:
    """Info message for CtiOs info"""
    def __init__(self, msg):
        Logger.info(msg)







