"""
@package base

@brief Base abstract class creating the base for WSDP clients and WSDP modules

Classes:
 - base::WSDPClient
 - base::WSDPFactory
 - base::WSDPBase
 - base::SestavyBase

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os
import json
from pathlib import Path
from abc import ABC, abstractmethod

from pywsdp.clients.factory import pywsdp
from pywsdp.base.logger import WSDPLogger
from pywsdp.base.exceptions import WSDPError


__version__ = '1.1'


class WSDPBase(ABC):
    """Abstraktni trida vytvarejici spolecne API pro WSDP sluzby.
    Odvozene tridy musi mit property skupina_sluzeb a nazev_sluzby.
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial=False):
        self.logger = WSDPLogger(self.nazev_sluzby)
        self.client = pywsdp.create(
            self.skupina_sluzeb, self.nazev_sluzby, creds, self.logger, trial
        )
        self._trial = trial
        self._creds = creds
        self._log_adresar = self._set_default_log_dir()

    @property
    def skupina_sluzeb(self):
        """Nazev typu skupiny sluzeb - ctiOS, sestavy, vyhledat, ciselniky etc.
        Nazev musi korespondovat se slovnikem WSDL endpointu - musi byt malymi pismeny.
        """
        return self._skupina_sluzeb

    @property
    def nazev_sluzby(self):
        """Nazev sluzby, napr. ctiOS, generujCenoveUdajeDleKu.
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """
        return self._nazev_sluzby

    @property
    def pristupove_udaje(self) -> dict:
        """Vraci pristupove udaje pod kterymi doslo k pripojeni ke sluzbe
        :rtype: dict
        """
        return self._creds

    @property
    def log_adresar(self) -> str:
        """Vypise cestu k adresari, ve kterem se budou vytvaret log soubory.
        :rtype: str
        """
        return self._log_adresar

    @log_adresar.setter
    def log_adresar(self, log_adresar: str):
        """Nastavi cestu k adresari, ve kterem se budou vytvaret log soubory.
        :param log_adresar: cesta k adresari
        """
        if not os.path.exists(log_adresar):
            os.makedirs(log_adresar)
        self.logger.set_directory(log_adresar)
        self._log_adresar = log_adresar

    @property
    def testovaci_mod(self) -> dict:
        """Vraci True/False podle toho zda uzivatel pristupuje k ostrym sluzbam (False)
        nebo ke sluzbam na zkousku (True)
        :rtype: bool
        """
        return self._trial

    @property
    def raw_xml(self):
        """Vraci surove XML ktere je vystupem ze sluzby, jeste nez bylo
        prevedeno na slovnik. U sluzby CtiOS vraci XML odpoved ve forme listu,
        rozdelenou po prvcich podle poctu dotazu na server.
        :rtype: list or str
        """
        return self.response_xml

    def posli_pozadavek(self, slovnik_identifikatoru: dict) -> dict:
        """Zpracuje vstupni parametry pomoci nektere ze sluzeb a
        vysledek ulozi do slovniku.
        :param slovnik: slovnik ve formatu specifickem pro danou sluzbu.
        :rtype: dict - XML odpoved rozparsovana do slovniku"
        """
        return self.client.send_request(slovnik_identifikatoru)

    def _set_default_log_dir(self) -> str:
        """Privatni metoda pro nasteveni logovaciho adresare."""

        def is_run_by_jupyter():
            import __main__ as main

            return not hasattr(main, "__file__")

        if is_run_by_jupyter():
            module_dir = os.path.abspath(
                os.path.join("../../", "pywsdp", "modules", self.nazev_sluzby)
            )
        else:
            module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            print(module_dir)
        log_dir = os.path.join(module_dir, "logs")
        print(log_dir)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.logger.set_directory(log_dir)
        return log_dir
    
    
class SestavyBase(WSDPBase):
    """Abstraktni trida definujici rozhrani pro praci se sestavami
    :param creds: slovnik pristupovych udaju [uzivatel, heslo]
    :param trial: True: dotazovani na SOAP sluzbu na zkousku, False: dotazovani na ostrou SOAP sluzbu
    """

    def __init__(self, creds: dict, trial=True):
        self._skupina_sluzeb = "sestavy"

        super().__init__(creds, trial=trial)

    @property
    @abstractmethod
    def nazev_sluzby(self):
        """Nazev sluzby, napr. generujCenoveUdajeDleKu.
        Nazev sluzby/metody uveden v Popisu webovych sluzeb pro uzivatele.
        """

    @property
    def skupina_sluzeb(self):
        """Nazev typu skupiny sluzeb - ctiOS, sestavy, vyhledat, ciselniky etc.
        Nazev musi korespondovat se slovnikem WSDL endpointu - musi byt malymi pismeny.
        """
        return self._skupina_sluzeb

    def nacti_identifikatory_z_json_souboru(self, json_path: str) -> dict:
        """Pripravi identifikatory z JSON souboru pro vstup do zavolani sluzby ze skupiny WSDP sestavy.
        :param json_path: cesta ke vstupnimu json souboru
        :rtype: dict
        """
        file = Path(json_path)
        if file.exists():
            with open(file) as f:
                data = json.load(f)
                return data
        else:
            raise WSDPError(self.logger, "Soubor nebyl nalezen!")

    def vypis_info_o_sestave(self, sestava: dict) -> dict:
        """S parametrem id sestavy zavola sluzbu SeznamSestav, ktera vypise info o sestave.
        :param sestava: slovnik vraceny pri vytvoreni sestavy
        :rtype: slovnik ve tvaru {'zprava': '',
         'idSestavy': '',
         'nazev': '',
         'pocetJednotek': '',
         'pocetStran': '',
         'cena': '',
         'datumPozadavku': '',
         'datumSpusteni': '',
         'datumVytvoreni': '',
         'stav': '',
         'format': '',
         'elZnacka': ''}
        """
        service = "seznamSestav"
        seznam_sestav = pywsdp.create(
            self._skupina_sluzeb,
            service,
            self.pristupove_udaje,
            self.logger,
            self.testovaci_mod,
        )
        return seznam_sestav.send_request(sestava["idSestavy"])

    def zauctuj_sestavu(self, sestava: dict) -> dict:
        """Vezme id sestavy z vytvorene sestavy a zavola sluzbu VratSestavu, ktera danou sestavu zauctuje.
        :param sestava: slovnik vraceny pri vytvoreni sestavy
        :rtype: slovnik ve tvaru {'zprava': '',
         'idSestavy': '',
         'nazev': '',
         'pocetJednotek': '',
         'pocetStran': '',
         'cena': '',
         'datumPozadavku': '',
         'datumSpusteni': '',
         'datumVytvoreni': '',
         'stav': '',
         'format': '',
         'elZnacka': '',
         'souborSestavy': ''}
        """
        service = "vratSestavu"
        vrat_sestavu = pywsdp.create(
            self._skupina_sluzeb,
            service,
            self.pristupove_udaje,
            self.logger,
            self.testovaci_mod,
        )
        return vrat_sestavu.send_request(sestava["idSestavy"])
    
    def vymaz_sestavu(self, sestava: dict) -> dict:
        """Vezme id sestavy z vytvorene sestavy a zavola sluzbu SmazSestavu, ktera danou sestavu z uctu smaze.
        :param sestava: slovnik vraceny pri vytvoreni sestavy
        :rtype: slovnik ve tvaru {'zprava': ''}
        """
        service = "smazSestavu"
        smaz_sestavu = pywsdp.create(
            self._skupina_sluzeb,
            service,
            self.pristupove_udaje,
            self.logger,
            self.testovaci_mod,
        )
        return smaz_sestavu.send_request(sestava["idSestavy"])
