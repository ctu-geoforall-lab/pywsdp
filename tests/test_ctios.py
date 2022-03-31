import sys
import os
import configparser
from shutil import copyfile
import xml.etree.ElementTree as et
import sqlite3
import json
import csv
import pytest

library_path = os.path.abspath(os.path.join('../'))
if library_path not in sys.path:
   sys.path.append(library_path)

from pywsdp.modules import CtiOS
from pywsdp import OutputFormat
from pywsdp.base.exceptions import WSDPRequestError


class TestCtiOS:

    service_dir = os.path.abspath(os.path.join(library_path, 'pywsdp', 'services'))
    service_group = service_name = "ctiOS"
    service_dir = os.path.abspath(os.path.join(service_dir, service_group))

    def test_00a_config_file(self):
        """Check if config file exists, check values."""
        config_path = os.path.join(
                self.service_dir, "config", "settings.ini"
            )
        # Check if condig file exists
        assert os.path.exists(config_path) == True

        # Check values in config file
        config = configparser.ConfigParser()
        config.read(config_path)     
        assert config["files"]["xml_template"] == "ctiOS.xml"
        assert config["service headers"]["content_type"] == "text/xml;charset=UTF-8"
        assert config["service headers"]["accept_encoding"] == "gzip,deflate"
        assert config["service headers"]["soap_action"] == "http://katastr.cuzk.cz/ctios/ctios"
        assert config["service headers"]["connection"] == "Keep-Alive"
        assert config["service headers"]["endpoint"] == "https://wsdptrial.cuzk.cz/trial/ws/ctios/2.8/ctios"

    def test_00b_mapping_file(self):
        """Check if mapping attributes json exists, check magic values."""
        mapping_attributes_path = os.path.join(
                self.service_dir, "config", "attributes_mapping.json"
            )
        # Check if json file exists
        assert os.path.exists(mapping_attributes_path) == True
        # Open mapping attributes json file
        with open(mapping_attributes_path) as json_file:
            dictionary = json.load(json_file)

        # Check values againts db columns
        db_path = os.path.join(library_path, 'data', 'input', 'ctios_template.db')
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute("PRAGMA read_committed = true;")
        cur.execute("""select * from {0}""".format("OPSUB"))
        col_names = list(map(lambda x: x[0], cur.description))

        for key, value in dictionary.items():
            if value in col_names:
                assert 1 == 1
            else:
                assert 0 == 1

    def test_00c_template_file(self):
        """Check if template file exists, check magic values."""
        template_path = os.path.join(
                self.service_dir, "config", "ctiOS.xml"
            )
        # Check if template file exists
        assert os.path.exists(template_path) == True

        # Check if CtiOsRequest tag is set up for $parameters
        tree = et.parse(template_path)
        root = tree.getroot()
        namespace = "{http://katastr.cuzk.cz/ctios/types/v2.8}"
        tags = root.findall(".//{}CtiOsRequest".format(namespace))
        assert tags[0].text == "$parameters"

    def test_01a_CtiOS_service(self):
        """Test the service itself, check http error code DB connection."""
        ctiOS = CtiOS()
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka"]
        }
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        status_code = ctiOS.otestuj_sluzbu()
        assert status_code == 200

    def test_01b_CtiOS_service_invalid_password(self):
        """Test the service itself, use invalid user/password, check if WSDPRequestError is raised.
        Send one posident with wrong set username and password."""
        ctiOS = CtiOS()
        ctiOS.uzivatel = "uzivatel" # wrong username
        ctiOS.heslo = "heslo" # wrong password
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka"]
        }
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        with pytest.raises(WSDPRequestError):
            ctiOS.otestuj_sluzbu()
        
    def test_02a_read_posidents_from_file(self):
        """Test reading posidents from json file."""
        json = os.path.join(library_path, 'data', 'input', 'ctios_template.json')
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_z_json_souboru(json)
        assert ctiOS.pocet_dotazovanych_identifikatoru == 10

    def test_02b_read_posidents_from_db(self):
        """Test reading posidents from db."""
        db_path = os.path.join(library_path, 'data', 'input', 'ctios_template.db')
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_z_databaze(db_path)
        assert ctiOS.pocet_dotazovanych_identifikatoru == 108

    def test_02c_read_posidents_from_db_sql(self):
        """Test reading posidents from db file. The select is specified by SQL query."""
        db_path = os.path.join(library_path, 'data', 'input', 'ctios_template.db')
        output_db = copyfile(db_path, os.path.join(library_path, 'data', 'output', 'ctios_template.db'))
        sql = "SELECT * FROM OPSUB order by ID LIMIT 10"
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_z_databaze(output_db, sql)
        assert ctiOS.pocet_dotazovanych_identifikatoru == 10

    def test_02d_read_posidents_from_dict(self):
        """Test reading posidents from dict."""
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka",
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka"
        ]}
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        assert ctiOS.pocet_dotazovanych_identifikatoru == 2

    def test_03a_request_XML(self):
        """Test if created XML from template is not empty and is valid, tag pOSIdent exists."""
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka",
        ]}
        namespace = "{http://katastr.cuzk.cz/ctios/types/v2.8}"
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        xmlattr = ctiOS.ctios.xml_attrs[0]
        request_xml = ctiOS.ctios._renderXML(parameters=xmlattr)
        root = et.fromstring(request_xml)
        # check tag with 'pOSIdent' name
        assert root.findall(".//{}pOSIdent".format(namespace)) is not None

    def test_03b_request_XML_invalid_version(self):
        """Modify request XML (invalid service version), send and check if WSDPRequestError is raised."""
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka",
        ]}
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        ctiOS.ctios._set_template_path(os.path.join(
            self.service_dir,
            "config",
            "ctiOS_invalid.xml",
        ))
        xmlattr = ctiOS.ctios.xml_attrs[0]
        request_xml = ctiOS.ctios._renderXML(parameters=xmlattr)
        with pytest.raises(WSDPRequestError):
            ctiOS.ctios._call_service(request_xml).text

    def test_03c_response_XML(self):
        """Check response XML (not empty, is valid)"""
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka",
        ]}
        namespace_ns0 = "{http://katastr.cuzk.cz/ctios/types/v2.8}"
        namespace_ns1 = "{http://katastr.cuzk.cz/commonTypes/v2.8}"
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        xmlattr = ctiOS.ctios.xml_attrs[0]
        request_xml = ctiOS.ctios._renderXML(parameters=xmlattr)
        response_xml = ctiOS.ctios._call_service(request_xml).text
        root = et.fromstring(response_xml)

        # Check tag with 'zprava' name
        tags = root.findall(".//{}zprava".format(namespace_ns1))
        assert tags[0].text == "Požadovaná akce byla úspěšně provedena."

        # check tags with 'os' name
        assert root.findall(".//{}os".format(namespace_ns0)) is not None

    def test_03d_parse_response_XML(self):
        """Parse response XML, check result dictionary"""
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka",
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka",
        "Vm+8vMmIsWsvcxR9zMDL9Cy+E0ZgHj9AJ3kwMqaLxguXn6wJcfM3e3LWpd7RzRxm3woikNUtGPF45crUFMpAsfsa/Bmx4YzTqTFCj0vhoQY=",
        "T/sOfNBmULfA5GzBpJRYu3UWEwhw4PFYydRQSh7x1PSc4RTRLXYaXTfpbt2Da17zSJPbQDKce+cHMMQVCVBRj9+U8wwRYYTBTgLsWbpMpuY=",
        "lWpFU3UmWlpSe8TtpUMRBCFflbRtrT1aEpzxnv1MEXnpCGhTicndBKbyJjsfMJMdgH+U78n9GU5DNm6bXxNhnC2JU2MIzwpJObcy4n2Baqk=",
        "mDkas+QvEOd4+XBxuIW4Da3aEEdBAod5OJM/9la0ivdkMk7DTs9DqRZEI5Lc3wAC7Yb1sw4kp/JEFP3nnG2ZcPT36EJYO+EfrC0OlzewTfM=",
        "7TsaZA7GFeEVxMscggvr2LkRAZwqfDywZ9HtkoX92fdNI/VFseD7SjfY8rJ7IlS7o2MG7D4mG56FZUTFOUWW7a5GeMmtDAasGLtodOgvIOA=",
        "yqpT3s/QygUWqCsg/azKypTOTOuJdbjB/16kQv0m5uugaHFJh8Mtp2i7sCdt71GRZixdYAzCVqEa4mNgvEjDECGf0Fby1B2nv1NdlyFQPrg=",
        "Z3anPBTLRy4YQTD0UgZkTJ+keVuWZ8j50lI8whQPyaERWuqwwnwsnvPL5JvmjhqosP5ukUJEFe29IEnCIx6/MSQ0jCVnAyGflCmCnQBnc3JQLWVD9vLnWZYbgp+9oL3r",
        "i0/Tr+VNmKgY+wJydNVJbCob8vQemEnjdn3A2r2ffhs8dz4IHH2H2AVcFvTyEOe3ci6MD33ZHXqEu8Lr8L1xtG3SHwhy2TBVM3bEa6vFpMbxj5wBXmFfT/QAGRrOqWBN",
        "/AOrBGOFR+4GtqsAvOXC/3kKd0OCEPBVRfEsIPHeW3CoGcU1dio8gmrulsH5/KEvySRvbRT2hlDOXICKukDLldMgNY5z+yASe8F1rqBlKug="
        ]}
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        xmlattr = ctiOS.ctios.xml_attrs[0]
        request_xml = ctiOS.ctios._renderXML(parameters=xmlattr)
        response_xml = ctiOS.ctios._call_service(request_xml).text
        dictionary = ctiOS.ctios._parseXML(response_xml)
        
        # Check first record in dictionary
        assert dictionary['uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka'] == \
        {'stavDat': '0', 'datumVzniku': '2000-01-01T00:00:00', 'priznakKontext': '3', 'rizeniIdVzniku': '26770653010', 'partnerBsm1': '29281934010', 'partnerBsm2': '344038746', 'opsubType': 'BSM', 'charOsType': '1', 'nazev': 'Čupa Josef a Kašná Marie', 'nazevU': 'CUPA JOSEF A KASNA MARIE', 'osId': '29281952010'}
        

    def test_04b_check_posident_types(self):
        """Test resulting statistics - posident types and number of requests on server."""
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka",
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka",
        "Vm+8vMmIsWsvcxR9zMDL9Cy+E0ZgHj9AJ3kwMqaLxguXn6wJcfM3e3LWpd7RzRxm3woikNUtGPF45crUFMpAsfsa/Bmx4YzTqTFCj0vhoQY=",
        "T/sOfNBmULfA5GzBpJRYu3UWEwhw4PFYydRQSh7x1PSc4RTRLXYaXTfpbt2Da17zSJPbQDKce+cHMMQVCVBRj9+U8wwRYYTBTgLsWbpMpuY=",
        "lWpFU3UmWlpSe8TtpUMRBCFflbRtrT1aEpzxnv1MEXnpCGhTicndBKbyJjsfMJMdgH+U78n9GU5DNm6bXxNhnC2JU2MIzwpJObcy4n2Baqk=",
        "mDkas+QvEOd4+XBxuIW4Da3aEEdBAod5OJM/9la0ivdkMk7DTs9DqRZEI5Lc3wAC7Yb1sw4kp/JEFP3nnG2ZcPT36EJYO+EfrC0OlzewTfM=",
        "7TsaZA7GFeEVxMscggvr2LkRAZwqfDywZ9HtkoX92fdNI/VFseD7SjfY8rJ7IlS7o2MG7D4mG56FZUTFOUWW7a5GeMmtDAasGLtodOgvIOA=",
        "yqpT3s/QygUWqCsg/azKypTOTOuJdbjB/16kQv0m5uugaHFJh8Mtp2i7sCdt71GRZixdYAzCVqEa4mNgvEjDECGf0Fby1B2nv1NdlyFQPrg=",
        "Z3anPBTLRy4YQTD0UgZkTJ+keVuWZ8j50lI8whQPyaERWuqwwnwsnvPL5JvmjhqosP5ukUJEFe29IEnCIx6/MSQ0jCVnAyGflCmCnQBnc3JQLWVD9vLnWZYbgp+9oL3r",
        "i0/Tr+VNmKgY+wJydNVJbCob8vQemEnjdn3A2r2ffhs8dz4IHH2H2AVcFvTyEOe3ci6MD33ZHXqEu8Lr8L1xtG3SHwhy2TBVM3bEa6vFpMbxj5wBXmFfT/QAGRrOqWBN",
        "/AOrBGOFR+4GtqsAvOXC/3kKd0OCEPBVRfEsIPHeW3CoGcU1dio8gmrulsH5/KEvySRvbRT2hlDOXICKukDLldMgNY5z+yASe8F1rqBlKug=",
        "mo3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q=",
        "mSH6sS5yv6vA2jEOtyHeXaXIJpC2m0Ai56aKzsVmEphUNyjFQYgC8MOLnu3+3Zugm8JQW2AJqEJYcSiqXdPbnb/03PKgyNkYWaS876wv0tg=",
        "mSH6sS5yv6vA2jEOtyHeXaXIJpC2m0Ai56aKzsVmEphUNyjFQYgC8MOLnu3+3Zugm8JQW2AJqEJYcSiqXdPbnb/03PKgyNkYWaS876wv0tg=",
        "mSH6sS5yv6vA2jEOtyHeXaXIJpC2m0Ai56aKzsVmEphUNyjFQYgC8MOLnu3+3Zugm8JQW2AJqEJYcSiqXdPbnb/03PKgyNkYWaS876wv0tg=="
        ]}
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        ctiOS.zpracuj_identifikatory()
        assert ctiOS.pocet_dotazovanych_identifikatoru == 15
        assert ctiOS.pocet_neplatnych_identifikatoru == 1
        assert ctiOS.pocet_expirovanych_identifikatoru == 0
        assert ctiOS.pocet_neexistujicich_os == 0
        assert ctiOS.pocet_uspesne_stazenych_os == 12
        assert ctiOS.pocet_odstranenych_duplicit == 2
        assert ctiOS.pocet_dotazu_na_server == 2

    def test_05a_write_output_json(self):
        """Check non empty, is valid, read json, check number of keys, posidents code"""
        json_file = os.path.join(library_path, 'data', 'input', 'ctios_template.json')
        vystupni_soubor = os.path.join(library_path, 'data', 'output', 'ctios.json')
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_z_json_souboru(json_file)
        vysledek = ctiOS.zpracuj_identifikatory()
        assert ctiOS.pocet_uspesne_stazenych_os == 10
        ctiOS.uloz_vystup(vysledek, vystupni_soubor, OutputFormat.Json)
        with open(vystupni_soubor) as json_file:
            dictionary = json.load(json_file)
            assert list(dictionary.keys()) == ["m+o3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q=",
        "mSH6sS5yv6vA2jEOtyHeXaXIJpC2m0Ai56aKzsVmEphUNyjFQYgC8MOLnu3+3Zugm8JQW2AJqEJYcSiqXdPbnb/03PKgyNkYWaS876wv0tg=",
        "xairWnG248pu7itR19AIT87mDFI8yY0K0ms7v/iDY679wQ4EN5bMhMPSTXxgWDxMWZ0IoV/ihjGkNMXeqXHrMZsEbHBTzD9RUIOXw5M1hmE=",
        "4m3Yuf1esDMzbgNGYW7kvzjlaZALZ3v3D7cXmxgCcFp0RerVtxqo8yb87oI0FBCtp49AycQ5NNI3vl+b+SEa+8SfmGU4sqBPH2pX/76wyBI=",
        "BBgBQ2wok0L43hEZUEeieq8FrrQsT1SHIrpQBRwgLw2uTvTsXvGloIYnr+7J2z6t/hadCsyhcbxgrf47ByzpbY5TjyiUPxyXhlS73MKArjs=",
        "ltTJU+/1imoqO4saz1ta1r88QGUxEkjRTfHUiC9Y9yfDKSM4c8soK/vz7bGd1JNwQPUiFayJQdLN0gPkusnnoNLo47RqbEoQxfg+eEuvTaQ=",
        "OlVCtLEjQ+aNPyQNdT0JZOkkxvwl8t9DllRl/HiNx7G3QFyZnvKA4e2LBTSX+YuK41/rSMvAnm63ZeWPyZQCX77GuP1GZwwf2hVkKzVY/94=",
        "KdSYyo8J1zUPVqxHUtY+tYA2w7krH9U+59hCYU8TXGZ06e74GGekPinyLtiSz+gO7ZmpWetCSaxvu1nXa6+t7w92wpqfa5jPpkfv5HF9MMA=",
        "5wQRil9Nd5KIrn5KWTf8+sksZslnMqy2tveDvYPIsd1cd9qHYs1V9d9uZVwBEVe5Sknvonhh+FDiaYEJa+RdHM3VtvGsIqsc2Hm3mX0xYfs=",
        "UKcYWvUUTpNi8flxUzlm+Ss5iq0JV3CiStJSAMOk6xHFQncZraFeO9yj8OGraKiDJ8eLB0FegdXYuyYWsEXiv2H9ws95ezlKNTqR6ze7aOnR3a7NWzWJfe+R5VHfU13+"]

    def test_05b_write_output_db(self):
        """Check non empty, is valid, read db, check number of keys, posidents code"""
        db_path = os.path.join(library_path, 'data', 'input', 'ctios_template.db')
        output_path = copyfile(db_path, os.path.join(library_path, 'data', 'output', 'ctios_template.db'))
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_z_databaze(output_path)
        vysledek = ctiOS.zpracuj_identifikatory()
        ctiOS.uloz_vystup(vysledek, output_path , OutputFormat.GdalDb)
        con = sqlite3.connect(output_path)
        cur = con.cursor()
        for row in cur.execute("SELECT count(*) FROM OPSUB"):
            assert row == (108,)

    def test_05c_write_output_csv(self):
        """Check non empty, is valid, read csv, check number of keys, posidents code"""
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka",
        ]}
        vystupni_soubor = os.path.join(library_path, 'data', 'output', 'ctios.csv')
        ctiOS = CtiOS()
        boolean = 0
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        vysledek = ctiOS.zpracuj_identifikatory()
        ctiOS.uloz_vystup(vysledek, vystupni_soubor, OutputFormat.Csv)
        with open(vystupni_soubor, mode='r') as csv_file:
            for line in csv.reader(csv_file):
                if line[0] == dictionary["posidents"][0]:
                    boolean = 1
        assert boolean == 1

