"""
@package modules.CtiOS

@brief Output formats for CtiOS module

Classes:
 - CtiOS::OutputFormat

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

from enum import Enum


class OutputFormat(Enum):
    """
    Implemented output formats for CtiOs service.
    """

    GdalDb = 1
    Json = 2
    Csv = 3
