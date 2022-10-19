"""
@package modules.SeznamSestav

@brief Public API for SesznamSestav module

Classes:
 - SeznamSestav::SeznamSestav

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

from pywsdp.base import WSDPBase


class SeznamSestav(WSDPBase):
    """Trida definujici rozhrani pro praci se sluzbou Seznam sestav.
    Pouzije se v pripade, kdy znam sestavu a chci tuto sluzbu zavolat samostatne.
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial:  dict=False):
        self._nazev_sluzby = "seznamSestav"
        self._skupina_sluzeb = "sestavy"

        super().__init__(creds, trial=trial)

    @property
    def nazev_sluzby(self):
        """
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._nazev_sluzby

    @property
    def skupina_sluzeb(self):
        """
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._skupina_sluzeb