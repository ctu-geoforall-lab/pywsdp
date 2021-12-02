"""
@package modules

@brief Trida typu fasady zastresujici modul generujici cenove udale dle k.u.

Tridy:
 - GenerujCenoveUdajeDleKu

Metody:
 - uzivatel - getter
 - heslo - getter
 - uzivatel(uzivatel) - setter
 - heslo(heslo) - setter
 - pristupove_udaje(uzivatel, heslo) - getter
 - log_adresar - getter
 - log_adresar(log_adresar) - setter
 - id_sestavy - getter
 - format_sestavy - getter
 - soubor_sestavy - getter
 - nacti_parametry_ze_slovniku(cenove_udaje_slovnik: dict)
 - nacti_parametry_ze_json_souboru(cesta_k_json_souboru: str)
 - vytvor_sestavu
 - vypis_info_o_sestave(sestava)
 - zauctuj_sestavu(sestava)
 - uloz_vystup(zauctovana_sestava, vystupni_adresar)
 - vymaz_sestavu(sestava)

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os
import json
from datetime import datetime
from pathlib import Path

from base.factory import pywsdp
from base.exceptions import WSDPError
from base.logger import WSDPLogger


class GenerujCenoveUdajeDleKu():
    """Trida typu fasady pro obsluhu generovani cenovych udaje dle k.u."""
    def __init__(self):
        # Nazev modulu
        self.nazev_modulu = 'GenerujCenoveUdajeDleKu'

        # Inicializace sluzeb
        self.cen_udaje = None
        self.seznam_sestav = None
        self.vrat_sestavu = None
        self.smaz_sestavu = None

        # Nastaveni logovani
        self.logger = WSDPLogger(self.nazev_modulu)
        self._log_adresar = self._set_default_log_dir()

        # Boolean pro mazani sestavy
        self.not_deleted = True

    @property
    def uzivatel(self):
        """Vypise uzivatelske jmeno k WSDP."""
        return self.cen_udaje.username

    @property
    def heslo(self):
        """Vypise heslo k WSDP."""
        return self.cen_udaje.password

    @uzivatel.setter
    def uzivatel(self, uzivatel):
        """Nastavi uzivatelske jmeno k WSDP."""
        self.cen_udaje.username(uzivatel)

    @heslo.setter
    def heslo(self, heslo):
        """Nastavi heslo k WSDP."""
        self.cen_udaje.password(heslo)

    @property
    def pristupove_udaje(self):
        """Vypise pristupove udaje k WSDP ve forme uzivatelskeho jmeno a hesla."""
        return (self.cen_udaje.username, self.cen_udaje.password)

    @property
    def log_adresar(self):
        """ Vypise cestu k adresari, ve kterem se budou vytvaret log soubory."""
        return self._log_adresar

    @log_adresar.setter
    def log_adresar(self, log_adresar):
        """Nastavi cestu k adresari, ve kterem se budou vytvaret log soubory."""
        self._ensure_dir_exists(log_adresar)
        self.logger.set_directory(log_adresar)
        self._log_adresar = log_adresar

    def nacti_parametry_ze_slovniku(self, cenove_udaje_slovnik):
        """Vezme parametry ze slovniku
        a vytvori instanci sluzby GenerujCenoveUdajeDleKu.
        Jedna se o slovnik ve formatu:
          {"katastrUzemiKod" : "732630",
          "rok" : "2020",
          "mesicOd" : "9",
          "mesicDo" : "12",
          "format" : "zip"}, kdy klice jsou pevne dane.
        """
        dictionary = {'generujCenoveUdajeDleKu': cenove_udaje_slovnik}
        self.cen_udaje = pywsdp.create(recipe=dictionary, logger=self.logger)

    def nacti_parametry_z_json_souboru(self, cesta_k_json_souboru):
        """Vezme parametry ze souboru typu *.JSON
        a vytvori instanci sluzby GenerujCenoveUdajeDleKu
        Vnitrek json souboru je ve tvaru slovniku:
          {"katastrUzemiKod" : "732630",
          "rok" : "2020",
          "mesicOd" : "9",
          "mesicDo" : "12",
          "format" : "zip"}, kdy klice jsou pevne dane.
        """
        file = Path(cesta_k_json_souboru)
        if file.exists():
            with open(file) as f:
                data = json.load(f)
                dictionary = {self.nazev_modulu: data}
        else:
            raise WSDPError(
                self.logger,
                "File is not found!"
                )
        dictionary = {self.name: dictionary}
        self.cen_udaje = pywsdp.create(recipe=dictionary)

    def vytvor_sestavu(self):
        """Zavola sluzbu GenerujCenoveUdajeDleKu, preda ji parametry
        a vytvori sestavu.
        Vraci info o vytvorene sestave ve forme slovniku:
        {'zprava': '',
         'idSestavy': '',
         'nazev': '',
         'datumPozadavku': '',
         'datumSpusteni': '',
         'stav': '',
         'format': ''}
        """
        return self.cen_udaje._process()

    def vypis_info_o_sestave(self, sestava):
        """Vezme id listiny z vytvorene sestavy a zavola sluzbu SeznamSestav,
        ktera vypise info o sestave.
        Vraci info o sestave ve forme slovniku.
        Odpoved je ve forme:
        {'zprava': '',
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
        self.parametry = {'seznamSestav': {'idSestavy': sestava["idSestavy"]}}
        self.seznam_sestav = pywsdp.create(recipe=self.parametry, logger=self.logger)
        self.seznam_sestav.username = self.uzivatel
        self.seznam_sestav.password = self.heslo
        return self.seznam_sestav._process()

    def zauctuj_sestavu(self, sestava):
        """Vezme id listiny z vytvorene sestavy a zavola sluzbu VratSestavu,
        ktera danou sestavu zauctuje.
        Vraci info o zauctovani sestavy ve forme slovniku:
        {'zprava': '',
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
         'souborSestavy': ''}"""
        self.parameters = {'vratSestavu': {'idSestavy':  sestava["idSestavy"]}}
        self.vrat_sestavu = pywsdp.create(recipe=self.parameters, logger=self.logger)
        self.vrat_sestavu.username = self.uzivatel
        self.vrat_sestavu.password = self.heslo
        return self.vrat_sestavu._process()

    def uloz_vystup(self, zauctovana_sestava, vystupni_adresar):
        """Vezme zakodovany soubor z vystupnich hodnot sluzby VratSestavu,
        rozkoduje ho a ulozi na disk.
        """
        datum = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
        vystupni_soubor = "cen_udaje_{}.{}".format(datum, zauctovana_sestava["format"])
        output = os.path.join(vystupni_adresar, vystupni_soubor)
        self.cen_udaje._write_output(output, zauctovana_sestava["souborSestavy"])
        return output

    def vymaz_sestavu(self, sestava):
        """Vezme id listiny z vytvorene sestavy, zavola sluzbu SmazSestavu,
        ktera danou sestavu smaze.
        Vraci info o smazani sestavy ve forme slovniku:
        {'zprava': ''}"""
        self.parameters = {'smazSestavu': {'idSestavy': sestava["idSestavy"]}}
        self.smaz_sestavu = pywsdp.create(recipe=self.parameters, logger=self.logger)
        self.smaz_sestavu.username = self.uzivatel
        self.smaz_sestavu.password = self.heslo
        self.not_deleted = False
        return self.smaz_sestavu._process()

    def _set_default_log_dir(self):
        """Method for getting default log dir"""
        def is_run_by_jupyter():
            import __main__ as main
            return not hasattr(main, '__file__')

        if is_run_by_jupyter():
            module_dir = os.path.abspath(os.path.join('../../', 'modules', self.nazev_modulu))
        else:
            module_dir = os.path.dirname(__file__)
        log_dir = os.path.join(module_dir, "logs")
        self._ensure_dir_exists(log_dir)
        self.logger.set_directory(log_dir)
        return log_dir

    def _ensure_dir_exists(self, directory):
        """Method for checking if dir exists.
        If does not exist, it creates a new dir"""
        if not os.path.exists(directory):
            os.makedirs(directory)

    def __del__(self):
        if self.not_deleted:
            self.smaz_sestavu()