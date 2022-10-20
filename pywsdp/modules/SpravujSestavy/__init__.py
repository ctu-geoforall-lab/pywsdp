"""
@package modules.SpravujSestavy

@brief Public API for Sestavy managing 

Classes:
 - SeznamSestav::SeznamSestav
 - VratSestavu::VratSestavu
 - SmazSestavu::SmazSestavu
 
(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

from pywsdp.base import WSDPBase


class SeznamSestav(WSDPBase):
    """Trida definujici rozhrani pro praci se sluzbou seznamSestav.
    Pouzije se v pripade, kdy znam sestavu a chci tuto sluzbu zavolat samostatne.

    :param creds:
    :param trial:
    """

    def __init__(self, creds: dict, trial: dict = False):
        self._nazev_sluzby = "seznamSestav"
        self._skupina_sluzeb = "sestavy"

        super().__init__(creds, trial=trial)


class VratSestavu(WSDPBase):
    """Trida definujici rozhrani pro praci se sluzbou vratSestavu.
    Pouzije se v pripade, kdy znam sestavu a chci tuto sluzbu zavolat samostatne.

    :param creds:
    :param trial:
    """

    def __init__(self, creds: dict, trial: dict = False):
        self._nazev_sluzby = "vratSestavu"
        self._skupina_sluzeb = "sestavy"

        super().__init__(creds, trial=trial)


class SmazSestavu(WSDPBase):
    """Trida definujici rozhrani pro praci se sluzbou smazSestavu.
    Pouzije se v pripade, kdy znam sestavu a chci tuto sluzbu zavolat samostatne.

    :param creds:
    :param trial:
    """

    def __init__(self, creds: dict, trial: dict = False):
        self._nazev_sluzby = "smazSestavu"
        self._skupina_sluzeb = "sestavy"

        super().__init__(creds, trial=trial)
