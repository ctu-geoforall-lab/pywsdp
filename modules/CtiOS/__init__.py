"""
@package modules

@brief Trida typu fasady zastresujici modul pro ziskani osobnich udaju
opravnenych subjektu.

Tridy:
 - CtiOS

Metody:
 - uzivatel - getter
 - heslo - getter
 - uzivatel(uzivatel) - setter
 - heslo(heslo) - setter
 - pristupove_udaje(uzivatel, heslo) - getter
 - log_adresar - getter
 - log_adresar(log_adresar) - setter
 - vezmi_identifikatory_ze_slovniku(ctios_slovnik: dict)
 - vezmi_identifikatory_z_json_souboru(cesta_k_json_souboru: str)
 - vezmi_identifikatory_z_databaze(cesta_k_databazi: str, sql: str)
 - zpracuj_identifikatory
 - uloz_vystup

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os

from base.factory import pywsdp
from base.exceptions import WSDPError
from base.logger import WSDPLogger


class CtiOS():
    """Trida typu fasady pro obsluhu ziskavani osobnich udaje opravnenych
    subjektu z KN"""
    def __init__(self):
        # Nazev modulu
        self.nazev_modulu = "CtiOS"

        # Inicializace sluzeb
        self.ctios = None

        # Nastaveni logovani
        self.logger = WSDPLogger(self.nazev_modulu)
        self._log_adresar = self._set_default_log_dir()

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

    def nacti_identifikatory_ze_slovniku(self, ctios_slovnik):
        """Vezme parametry ze slovniku
        a vytvori instanci sluzby CtiOSDict
        Jedna se o slovnik ve formatu:
        {"posidents" : [pseudokod1, pseudokod2...]}.
        """
        dictionary = {"ctiOSDict": ctios_slovnik}
        self.ctios = pywsdp.create(recipe=dictionary, logger=self.logger)

    def nacti_identifikatory_z_json_souboru(self, cesta_k_json_souboru):
        """Vezme parametry ze souboru typu *.JSON
        a vytvori instanci sluzby CtiOSJson
        Vnitrek json souboru je ve tvaru slovniku:
        {"posidents" : [pseudokod1, pseudokod2...]}.
        """
        dictionary = {"ctiOSJson": cesta_k_json_souboru}
        self.ctios = pywsdp.create(recipe=dictionary, logger=self.logger)

    def nacti_identifikatory_z_databaze(self, cesta_k_databazi, sql_dotaz=None):
        """Vezme parametry ze souboru typu *.db, ktery byl vytvoren z VFK souboru,
        a vytvori instanci sluzby CtiOSDb. Vstupem muze byt sql_dotaz pro
        vyber identifikatoru, prikladem: "SELECT * FROM OPSUB order by ID LIMIT 10".
        """
        if sql_dotaz:
            dictionary = {"ctiOSDb": [cesta_k_databazi, sql_dotaz]}
        else:
            dictionary = {"ctiOSDb": cesta_k_databazi}
        self.ctios = pywsdp.create(recipe=dictionary, logger=self.logger)

    def zpracuj_identifikatory(self):
        """Zpracuje vstupni parametry pomoci sluzby CtiOS a vysledne osobni udaje
        opravnenych subjektu ulozi do slovniku.
        V pripade vstupu ve forme databaze navic updatuje ziskanymi osobnimi
        udaji vstupni databazi.
        """
        return self.ctios._process()

    def uloz_vystup(self, osobni_udaje, format_souboru, vystupni_adresar):
        """Konvertuje osobni udaje typu slovnik do souboru o definovanem
        formatu a soubor ulozi do definovaneho vystupniho adresare.
        """
        format_souboru = format_souboru.lower()
        if format_souboru == "json":
            output = self.ctios._write_output_to_json(vystupni_adresar, osobni_udaje)
        elif format_souboru == "csv":
            output = self.ctios._write_output_to_csv(vystupni_adresar, osobni_udaje)
        else:
            raise WSDPError(
                self.ctios.logger,
                "Format {} is not supported".format(format_souboru)
            )
        return output

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