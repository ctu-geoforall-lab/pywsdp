import os
import sys
import math
import json
import csv
import sqlite3
import pytest

library_path = os.path.abspath(os.path.join("../"))
if library_path not in sys.path:
    sys.path.append(library_path)

from pywsdp.modules import CtiOS
from pywsdp.modules import GenerujCenoveUdajeDleKu
from pywsdp.modules.SpravujSestavy import SeznamSestav, VratSestavu, SmazSestavu
from pywsdp.modules.CtiOS import OutputFormat
from pywsdp.base.exceptions import WSDPRequestError

creds_test = ["WSTEST", "WSHESLO"]

# cesty
json_path_ctios = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "data", "input", "ctios_template_all.json")
)

db_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "data", "input", "ctios_template.db")
)

json_path_generujCen = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "data",
        "input",
        "generujCenoveUdajeDleKu_template.json",
    )
)

vystupni_adresar = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "data", "output")
)

# definice parametru
parametry_ctiOS_dict = {
    "pOSIdent": [
        "im+o3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q",
        "4m3Yuf1esDMzbgNGYW7kvzjlaZALZ3v3D7cXmxgCcFp0RerVtxqo8yb87oI0FBCtp49AycQ5NNI3vl+b+SEa+8SfmGU4sqBPH2pX/76wyB",
        "im+o3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q",
        "4m3Yuf1esDMzbgNGYW7kvzjlaZALZ3v3D7cXmxgCcFp0RerVtxqo8yb87oI0FBCtp49AycQ5NNI3vl+b+SEa+8SfmGU4sqBPH2pX/76wyBI",
        "5wQRil9Nd5KIrn5KWTf8+sksZslnMqy2tveDvYPIsd1cd9qHYs1V9d9uZVwBEVe5Sknvonhh+FDiaYEJa+RdHM3VtvGsIqsc2Hm3mX0xYfs=",
        "UKcYWvUUTpNi8flxUzlm+Ss5iq0JV3CiStJSAMOk6xHFQncZraFeO9yj8OGraKiDJ8eLB0FegdXYuyYWsEXiv2H9ws95ezlKNTqR6ze7aOnR3a7NWzWJfe+R5VHfU13+",
    ]
}

# zpracovani generovani cenovych udaje pomoci samostatnych modulu
parametry_generujCen_dict = {
    "katastrUzemiKod": 732630,
    "rok": 2020,
    "mesicOd": 9,
    "mesicDo": 12,
    "format": "zip",
}


class TestModules:
    """
    Check connection to services.
    """

    def test_00a_ctiOS_module(self):
        """Check if we are able to connect to CtiOS module."""
        try:
            ctios = CtiOS(creds_test, trial=True)
        except WSDPRequestError:
            with WSDPRequestError:
                pytest.fail("Failed to get response from the service.")
        assert ctios.nazev_sluzby == "ctiOS"
        assert ctios.skupina_sluzeb == "ctios"

    def test_00b_generujCenoveUdajeDleKu_module(self):
        """Check if we are able to connect to GenerujCenoveUdajeDleKu module."""
        try:
            cen_udaje = GenerujCenoveUdajeDleKu(creds_test, trial=True)
        except WSDPRequestError:
            with WSDPRequestError:
                pytest.fail("Failed to get response from the service.")
        assert cen_udaje.nazev_sluzby == "generujCenoveUdajeDleKu"
        assert cen_udaje.skupina_sluzeb == "sestavy"

    def test_00c_seznamSestav_module(self):
        """Check if we are able to connect to seznamSestav module."""
        try:
            seznam = SeznamSestav(creds_test, trial=True)
        except WSDPRequestError:
            with WSDPRequestError:
                pytest.fail("Failed to get response from the service.")
        assert seznam.nazev_sluzby == "seznamSestav"
        assert seznam.skupina_sluzeb == "sestavy"

    def test_00d_vratSestavu_module(self):
        """Check if we are able to connect to vratSestavu module."""
        try:
            vrat = VratSestavu(creds_test, trial=True)
        except WSDPRequestError:
            with WSDPRequestError:
                pytest.fail("Failed to get response from the service.")
        assert vrat.nazev_sluzby == "vratSestavu"
        assert vrat.skupina_sluzeb == "sestavy"

    def test_00e_smazSestavu_module(self):
        """Check if we are able to connect to CtiOS service."""
        try:
            smaz = SmazSestavu(creds_test, trial=True)
        except WSDPRequestError:
            with WSDPRequestError:
                pytest.fail("Failed to get response from the service.")
        assert smaz.nazev_sluzby == "smazSestavu"
        assert smaz.skupina_sluzeb == "sestavy"


class TestInputsProcessing:
    """
    Check the server response based on different input attributes.
    """

    def test_01a_ctiOS_dict(self):
        "Check processing of dict data"
        ctios = CtiOS(creds_test, trial=True)
        slovnik, slovnik_chybnych = ctios.posli_pozadavek(parametry_ctiOS_dict)
        assert slovnik_chybnych == {
            "im+o3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q": "NEPLATNY_IDENTIFIKATOR",
            "4m3Yuf1esDMzbgNGYW7kvzjlaZALZ3v3D7cXmxgCcFp0RerVtxqo8yb87oI0FBCtp49AycQ5NNI3vl+b+SEa+8SfmGU4sqBPH2pX/76wyB": "NEPLATNY_IDENTIFIKATOR",
        }
        assert ctios.client.number_of_posidents == 6  # celkovy pocet identifikatoru
        assert (
            ctios.client.number_of_posidents - ctios.client.number_of_posidents_final
            == 1
        )  # odstranene duplicity
        assert (
            math.ceil(
                ctios.client.number_of_posidents_final
                / ctios.client.posidents_per_request
            )
            == 1
        )  # pocet dotazu na server
        assert ctios.client.counter.uspesne_stazeno == 3
        assert ctios.client.counter.neplatny_identifikator == 2
        assert ctios.client.counter.expirovany_identifikator == 0
        assert ctios.client.counter.opravneny_subjekt_neexistuje == 0

    def test_01b_ctiOS_json(self):
        "Check processing of input json"
        ctios = CtiOS(creds_test, trial=True)
        parametry_ctiOS_json = ctios.nacti_identifikatory_z_json_souboru(
            json_path_ctios
        )
        slovnik, slovnik_chybnych = ctios.posli_pozadavek(parametry_ctiOS_json)
        assert slovnik_chybnych == {
            "jal/5GuoZ+/s2QkvrawUhJRYZr6wjBtFT3a5YfFpLfO0Sl6HMqxe2WPzMAmQYk/+o12GBZTFDXRnpHAquQOJB056iYSc7j1gQ36LCXfNkZM=": "OPRAVNENY_SUBJEKT_NEEXISTUJE",
            "gJpTEEtVTpfXe97BVKt4Q8yLgTdQVjd/jf9HRypwbxP78KrooS73YQ2tQB/FZOg0JTXtrjtxjFV/Da85vocyS8niP19J9aLOj6hkcMdkMvU=": "OPRAVNENY_SUBJEKT_NEEXISTUJE",
        }
        assert ctios.client.number_of_posidents == 50  # celkovy pocet identifikatoru
        assert ctios.client.counter.uspesne_stazeno == 48
        assert ctios.client.counter.opravneny_subjekt_neexistuje == 2

    def test_01c_ctiOS_db(self):
        "Check processing of input db"
        ctios = CtiOS(creds_test, trial=True)
        parametry_ctiOS_db = ctios.nacti_identifikatory_z_db(db_path)
        slovnik, slovnik_chybnych = ctios.posli_pozadavek(parametry_ctiOS_db)
        assert ctios.client.number_of_posidents == 108  # celkovy pocet identifikatoru
        assert ctios.client.counter.uspesne_stazeno == 108

    def test_01d_ctiOS_db_sql(self):
        """Test reading posidents from db file. The select is specified by SQL query."""
        ctios = CtiOS(creds_test, trial=True)
        parametry_ctiOS_db = ctios.nacti_identifikatory_z_db(
            db_path, "SELECT * FROM OPSUB order by ID LIMIT 10"
        )
        slovnik, slovnik_chybnych = ctios.posli_pozadavek(parametry_ctiOS_db)
        assert ctios.client.number_of_posidents == 10  # celkovy pocet identifikatoru
        assert ctios.client.counter.uspesne_stazeno == 10

    def test_01a_generujCenoveUdajeDleKu_dict(self):
        "Check processing of input dict using independent modules"
        gen = GenerujCenoveUdajeDleKu(creds_test, trial=True)
        ses = gen.posli_pozadavek(parametry_generujCen_dict)
        assert ses["nazev"] == "Cenové údaje podle katastrálního území"
        seznam = SeznamSestav(creds_test, trial=True)
        info = seznam.posli_pozadavek(ses["id"])
        assert info["nazev"] == "Cenové údaje podle katastrálního území"
        vrat = VratSestavu(creds_test, trial=True)
        zauctovani = vrat.posli_pozadavek(ses["id"])
        assert zauctovani["nazev"] == "Cenové údaje podle katastrálního území"
        smaz = SmazSestavu(creds_test, trial=True)
        smazani = smaz.posli_pozadavek(ses["id"])
        assert smazani == {"zprava": "Požadovaná akce byla úspěšně provedena."}

    def test_01b_generujCenoveUdajeDleKu_json(self):
        "Check processing of input json using inner GenerujCenoveUdajeDleKu methods"
        gen = GenerujCenoveUdajeDleKu(creds_test, trial=True)
        parametry_generujCen_json = gen.nacti_identifikatory_z_json_souboru(
            json_path_generujCen
        )
        ses = gen.posli_pozadavek(parametry_generujCen_json)
        assert ses["nazev"] == "Cenové údaje podle katastrálního území"
        info = gen.vypis_info_o_sestave(ses)
        assert info["nazev"] == "Cenové údaje podle katastrálního území"
        zauctovani = gen.zauctuj_sestavu(ses)
        assert zauctovani["nazev"] == "Cenové údaje podle katastrálního území"
        smazani = gen.vymaz_sestavu(ses)
        assert smazani == {"zprava": "Požadovaná akce byla úspěšně provedena."}


class TestOutputs:
    """
    Check the module outputs.
    """

    def test_02a_ctiOS_json(self):
        "Check the module output to json"
        ctios = CtiOS(creds_test, trial=True)
        slovnik, slovnik_chybnych = ctios.posli_pozadavek(parametry_ctiOS_dict)
        vystup, vystup_chybnych = ctios.uloz_vystup(
            slovnik, vystupni_adresar, OutputFormat.Json, slovnik_chybnych
        )
        assert os.path.exists(vystup) == True
        assert os.path.exists(vystup_chybnych) == True

        with open(vystup) as json_file:
            dictionary = json.load(json_file)
            assert list(dictionary.keys()) == [
                "4m3Yuf1esDMzbgNGYW7kvzjlaZALZ3v3D7cXmxgCcFp0RerVtxqo8yb87oI0FBCtp49AycQ5NNI3vl+b+SEa+8SfmGU4sqBPH2pX/76wyBI",
                "5wQRil9Nd5KIrn5KWTf8+sksZslnMqy2tveDvYPIsd1cd9qHYs1V9d9uZVwBEVe5Sknvonhh+FDiaYEJa+RdHM3VtvGsIqsc2Hm3mX0xYfs=",
                "UKcYWvUUTpNi8flxUzlm+Ss5iq0JV3CiStJSAMOk6xHFQncZraFeO9yj8OGraKiDJ8eLB0FegdXYuyYWsEXiv2H9ws95ezlKNTqR6ze7aOnR3a7NWzWJfe+R5VHfU13+",
            ]
        os.remove(vystup)

        with open(vystup_chybnych) as json_file:
            dictionary = json.load(json_file)
            assert list(dictionary.keys()) == [
                "im+o3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q",
                "4m3Yuf1esDMzbgNGYW7kvzjlaZALZ3v3D7cXmxgCcFp0RerVtxqo8yb87oI0FBCtp49AycQ5NNI3vl+b+SEa+8SfmGU4sqBPH2pX/76wyB",
            ]
        if vystup_chybnych:
            os.remove(vystup_chybnych)

    def test_02b_ctiOS_csv(self):
        "Check the module output to csv"
        ctios = CtiOS(creds_test, trial=True)
        slovnik, slovnik_chybnych = ctios.posli_pozadavek(parametry_ctiOS_dict)
        vystup, vystup_chybnych = ctios.uloz_vystup(
            slovnik, vystupni_adresar, OutputFormat.Csv, slovnik_chybnych
        )
        assert os.path.exists(vystup) == True

        with open(vystup, mode="r") as csv_file:
            for line in csv.reader(csv_file):
                # prvni spravny identifikator ze seznamu
                if line[0] == parametry_ctiOS_dict["pOSIdent"][3]:
                    boolean = 1
        assert boolean == 1

        os.remove(vystup)
        if vystup_chybnych:
            os.remove(vystup_chybnych)

    def test_02c_ctiOS_db(self):
        "Check the module output to SQLite DB"
        ctios = CtiOS(creds_test, trial=True)
        parametry_ctiOS_db = ctios.nacti_identifikatory_z_db(db_path)
        slovnik, slovnik_chybnych = ctios.posli_pozadavek(parametry_ctiOS_db)
        vystup, vystup_chybnych = ctios.uloz_vystup(
            slovnik, vystupni_adresar, OutputFormat.GdalDb, slovnik_chybnych
        )
        assert os.path.exists(vystup) == True

        con = sqlite3.connect(vystup)
        cur = con.cursor()
        for row in cur.execute("SELECT count(*) FROM OPSUB"):
            assert row == (108,)
        con.close()

        os.remove(vystup)
        if vystup_chybnych:
            os.remove(vystup_chybnych)

    def test_02a_generujCenoveUdajeDleKu(self):
        "Check the module output to zip"
        gen = GenerujCenoveUdajeDleKu(creds_test, trial=True)
        ses = gen.posli_pozadavek(parametry_generujCen_dict)
        info = gen.vypis_info_o_sestave(ses)
        zauctovani = gen.zauctuj_sestavu(ses)
        cesta = gen.uloz_vystup(zauctovani, vystupni_adresar)
        assert os.path.exists(cesta) == True
        os.remove(cesta)
        smazani = gen.vymaz_sestavu(ses)
        assert smazani == {"zprava": "Požadovaná akce byla úspěšně provedena."}
