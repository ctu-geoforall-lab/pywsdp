"""
@package modules.CtiOS

@brief Public API for CtiOS module

Classes:
 - CtiOS:CtiOS

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os
import csv
import json
from pathlib import Path
from datetime import datetime
import shutil

from pywsdp.base import WSDPBase
from pywsdp.base.exceptions import WSDPError
from pywsdp.modules.CtiOS.formats import OutputFormat
from pywsdp.modules.CtiOS.helpers import AttributeConverter, DbManager


# Mapping dictionary for conversion from XML response and DB Gdal SQLITE db
_XML2DB_mapping = {
    "priznakKontext": "PRIZNAK_KONTEXTU",
    "partnerBsm1": "ID_JE_1_PARTNER_BSM",
    "partnerBsm2": "ID_JE_2_PARTNER_BSM",
    "charOsType": "CHAROS_KOD",
    "kodAdresnihoMista": "KOD_ADRM",
    "idNadrizenePravnickeOsoby": "ID_NADRIZENE_PO",
}


class CtiOS(WSDPBase):
    """Trida definujici rozhrani pro praci se sluzbou ctiOS.

    :param creds:
    :param trial:

    """

    def __init__(self, creds: dict, trial: dict = False):
        self._nazev_sluzby = "ctiOS"
        self._skupina_sluzeb = "ctios"
        self._input_db = None

        super().__init__(creds, trial=trial)

    def nacti_identifikatory_z_db(self, db_path: str, sql_dotaz=None) -> dict:
        """Pripravi identifikatory z SQLITE databaze pro vstup do zavolani sluzby ctiOS.

        :param db_path: cesta k SQLITE databazi ziskane rozbalenim VFK souboru
        :param sql_dotaz: omezeni zpracovavanych identifikatoru pres SQL dotaz, napr. SELECT * FROM OPSUB order by ID LIMIT 10
        :return: data pro vstup do sluzby ctiOS
        """
        db = DbManager(db_path, self.logger)  # pripojeni k SQLite databazi

        if sql_dotaz:
            posidents = db.get_posidents_from_db(sql_dotaz)
        else:
            posidents = db.get_posidents_from_db()

        self._input_db = db_path  # zpristupneni cesty k vstupni databazi

        db.close_connection()
        return {"pOSIdent": posidents}

    def nacti_identifikatory_z_json_souboru(self, json_path: str) -> dict:
        """Pripravi identifikatory z JSON souboru pro vstup do zavolani sluzby ctiOS.

        :param json_path: cesta k JSON souboru s pseudonymizovanymi identifikatory.
        :return: data pro vstup do sluzby ctiOS

        """
        file = Path(json_path)
        if file.exists():
            with open(file) as f:
                data = json.load(f)
                return data
        else:
            raise WSDPError(self.logger, "File is not found!")

    def posli_pozadavek(self, slovnik_identifikatoru: dict) -> dict:
        """Zpracuje vstupni parametry pomoci nektere ze sluzeb a
        vysledek ulozi do slovniku. Zaroven vypocte zaloguje statistiku procesu.

        :param slovnik: vstupni parametry specificke pro danou sluzbu.
        :return: objekt zeep knihovny prevedeny na slovnik a upraveny pro vystup
        """
        response, response_errors = self.client.send_request(slovnik_identifikatoru)
        self.client.log_statistics()
        return response, response_errors

    def uloz_vystup(
        self,
        vysledny_slovnik: dict,
        vystupni_adresar: str,
        format_souboru: OutputFormat,
        slovnik_chybnych_identifikatoru: dict = None,
    ):
        """Konvertuje osobni udaje typu slovnik ziskane ze sluzby ctiOS do souboru o definovanem
        formatu a soubor ulozi do definovaneho vystupniho adresare. Pokud adresar neexistuje, vytvori ho.

        :param vysledny_slovnik: slovnik vraceny pro uspesne zpracovane identifikatory
        :param vystupni_adresar: cesta k vystupnimu adresari
        :param format_souboru: format typu OutputFormat.GdalDb, OutputFormat.Json nebo OutputFormat.Csv
        :param slovnik_chybnych_identifikatoru: slovnik vraceny pro neuspesne zpracovane identifikatory
        :return: cesta k vystupnimu souboru
        """
        cas = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
        vystupni_cesta_chybnych = None

        # kontrola existence vystupniho souboru
        if os.path.exists(vystupni_adresar) == False:
            try:
                os.mkdir(vystupni_adresar)
            except:
                raise WSDPError(self.logger, "Cilovy adresar se nepodarilo vytvorit.")

        if format_souboru == OutputFormat.GdalDb:
            vystupni_soubor = "".join(["ctios_", cas, ".db"])
            vystupni_cesta = os.path.join(vystupni_adresar, vystupni_soubor)
            try:
                shutil.copyfile(
                    self._input_db, vystupni_cesta
                )  # prekopirovani souboru db do cilove cesty
            except:
                raise WSDPError(self.logger, "Soubor nelze ulozit do ciloveho adresare")
            db = DbManager(vystupni_cesta, self.logger)
            db.add_column_to_db("OS_ID", "text")
            input_db_columns = db.get_columns_names()
            db_dictionary = AttributeConverter(
                _XML2DB_mapping, vysledny_slovnik, input_db_columns, self.logger
            ).convert_attributes()
            db.update_rows_in_db(db_dictionary)
            db.close_connection()
        elif format_souboru == OutputFormat.Json:
            vystupni_soubor = "".join(["ctios_", cas, ".json"])
            vystupni_cesta = os.path.join(vystupni_adresar, vystupni_soubor)
            try:
                with open(vystupni_cesta, "w", newline="", encoding="utf-8") as f:
                    json.dump(vysledny_slovnik, f, ensure_ascii=False)
            except:
                raise WSDPError(self.logger, "Soubor nelze ulozit do ciloveho adresare")
        elif format_souboru == OutputFormat.Csv:
            vystupni_soubor = "".join(["ctios_", cas, ".csv"])
            vystupni_cesta = os.path.join(vystupni_adresar, vystupni_soubor)
            header = sorted(
                set(i for b in map(dict.keys, vysledny_slovnik.values()) for i in b)
            )
            try:
                with open(vystupni_cesta, "w", newline="") as f:
                    write = csv.writer(f)
                    write.writerow(["posident", *header])
                    for a, b in vysledny_slovnik.items():
                        write.writerow([a] + [b.get(i, "") for i in header])
            except:
                raise WSDPError(self.logger, "Soubor nelze ulozit do ciloveho adresare")
        else:
            raise WSDPError(
                self.logger, "Format {} neni podporovan".format(format_souboru)
            )
        # logovani ulozeni vystupu
        self.logger.info("Vystup byl ulozen zde: {}".format(vystupni_cesta))

        # zapsani chybnych identifikatoru do json souboru
        if slovnik_chybnych_identifikatoru:
            vystupni_soubor = "".join(["ctios_errors_", cas, ".json"])
            vystupni_cesta_chybnych = os.path.join(vystupni_adresar, vystupni_soubor)
            with open(vystupni_cesta_chybnych, "w", newline="", encoding="utf-8") as f:
                json.dump(slovnik_chybnych_identifikatoru, f, ensure_ascii=False)
                self.logger.info(
                    "Zaznam o nezpracovanych identifikatorech byl ulozen zde: {}".format(
                        vystupni_cesta_chybnych
                    )
                )
        return vystupni_cesta, vystupni_cesta_chybnych

    def vypis_statistiku(self):
        """Vytiskne statistiku zpracovanych pseudonymizovanych identifikatoru (POSIdentu).
        Pocet neplatnych identifikatoru = pocet POSIdentu, ktere nebylo mozne rozsifrovat;
        Pocet expirovanych identifikatoru = pocet POSIdentu, kterym vyprsela casova platnost;
        Pocet identifikatoru k neexistujicim OS = pocet POSIdentu, ktere obsahuji neexistujici OS ID (neni na co je napojit);
        Pocet uspesne zpracovanych identifikatoru = pocet identifikatoru, ke kterym byly uspesne zjisteny osobni udaje;
        Pocet odstranenych duplicit = pocet vstupnich zaznamu, ktere byly pred samotnym zpracovanim smazany z duvodu duplicit;
        Pocet dotazu na server = pocet samostatnych dotazu, do kterych byl pozadavek rozdelen
        """
        self.client.print_statistics()
