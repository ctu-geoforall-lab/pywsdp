import sys
import os
import pytest
import configparser
from pathlib import Path
from shutil import copyfile

sys.path.insert(0, str(Path(__file__).parent.parent))
from pywsdp.modules import CtiOS


class TestCtiOS:

    service_group = service_name = "ctiOS"
    library_path = os.path.abspath(os.path.join('../../'))
    if library_path not in sys.path:
       sys.path.append(library_path)
    service_dir = os.path.abspath(os.path.join(library_path, 'pywsdp', 'services', 'ctiOS'))

    def test_config_file(self):
        """Read config, check values."""
        config_path = os.path.join(
                self.service_dir, "config", "settings.ini"
            )
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # check values
        assert config["files"]["xml_template"] == "ctiOS.xml"
        assert config["service headers"]["content_type"] == "text/xml;charset=UTF-8"
        assert config["service headers"]["accept_encoding"] == "gzip,deflate"
        assert config["service headers"]["soap_action"] == "http://katastr.cuzk.cz/ctios/ctios"
        assert config["service headers"]["connection"] == "Keep-Alive"
        assert config["service headers"]["endpoint"] == "https://wsdptrial.cuzk.cz/trial/ws/ctios/2.8/ctios"

    def test_CtiOS_service(self):
        """Test the service itself, use invalid user/password, check http error code DB connection.
        Send one posident with wrong set username and password"""
        config_path = os.path.join(
                self.service_dir, "config", "settings.ini"
            )
        config = configparser.ConfigParser()
        config.read(config_path)
        
        ctiOS = CtiOS()
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka"]
        }
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        status = ctiOS.otestuj_sluzbu()
        print(status)
        assert status == 200
         
    def test_CtiOS_service_invalid_password(self):
        """Test the service itself, use invalid user/password, check http error code DB connection.
        Send one posident with wrong set username and password"""
        config_path = os.path.join(
                self.service_dir, "config", "settings.ini"
            )
        config = configparser.ConfigParser()
        config.read(config_path)
        
        ctiOS = CtiOS()
        ctiOS.uzivatel = "uzivatel"
        ctiOS.heslo = "heslo"
        dictionary = {"posidents" : [
        "uecJ/wWk2Ej6CAnwe3i0y0jfrp9Xr1oMVJ+9kLKpkU8trb/GSsJmcvNw7XJ0dzNpkKLYrpaxDPIVMKGKnG/ZMzSYtEOoqKGnRHhbt/PXjUr/RJzL4O5LlsS30GNP3Kka"]
        }
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        status = ctiOS.otestuj_sluzbu()
        print(status)
        assert status != 200

    def test_template_file_exists(self):
        """Check if template file exists"""
        template_path = os.path.join(
                self.service_dir, "config", "ctiOS.xml"
            )
        assert os.path.exists(template_path) == True

    def test_mapping_file_exists(self):
        """Cehck if mapping attributes file exists."""
        mapping_attributes_path = os.path.join(
                self.service_dir, "config", "attributes_mapping.json"
            )
        assert os.path.exists(mapping_attributes_path) == True

    def test_read_posidents_from_file(self):
        """Test reading posidents from json file."""
        json = os.path.join(self.library_path, 'data', 'input', 'ctios_template.json')
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_z_json_souboru(json)
        # dopsat property na pocet posidentu - len(self._get_parameters())
        assert len(ctiOS.pocet_uspesne_stazenych) == 10

    def test_read_posidents_from_db(self):
        """Test reading posidents from db (50)."""
        db_path = os.path.join(self.library_path, 'data', 'input', 'ctios_template.db')
        output_db = copyfile(db_path, os.path.join(self.library_path, 'data', 'output', 'ctios_template.db'))
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_z_databaze(output_db)
        # dopsat property na pocet posidentu - len(self._get_parameters())
        assert len(ctiOS.pocet_uspesne_stazenych) == 50

    def test_read_posidents_from_db_sql(self):
        """Test reading posidents from db file (10)."""
        db_path = os.path.join(self.library_path, 'data', 'input', 'ctios_template.db')
        output_db = copyfile(db_path, os.path.join(self.library_path, 'data', 'output', 'ctios_template.db'))
        sql = "SELECT * FROM OPSUB order by ID LIMIT 10"
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_z_databaze(output_db, sql)
        # dopsat property na pocet posidentu - len(self._get_parameters())
        assert len(ctiOS.pocet_uspesne_stazenych) == 10

    def test_read_posidents_from_dict(self):
        """Test reading posidents from dict file, adding expired posidents (2), nonvalid posidents (1) and duplicit (1)."""
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
        "m+o3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q=",
        "mSH6sS5yv6vA2jEOtyHeXaXIJpC2m0Ai56aKzsVmEphUNyjFQYgC8MOLnu3+3Zugm8JQW2AJqEJYcSiqXdPbnb/03PKgyNkYWaS876wv0tg=",
        "mSH6sS5yv6vA2jEOtyHeXaXIJpC2m0Ai56aKzsVmEphUNyjFQYgC8MOLnu3+3Zugm8JQW2AJqEJYcSiqXdPbnb/03PKgyNkYWaS876wv0tg=",
        "mSH6sS5yv6vA2jEOtyHeXaXIJpC2m0Ai56aKzsVmEphUNyjFQYgC8MOLnu3+3Zugm8JQW2AJqEJYcSiqXdPbnb/03PKgyNkYWaS876wv0tg=="
        ]}
        ctiOS = CtiOS()
        ctiOS.nacti_identifikatory_ze_slovniku(dictionary)
        # dopsat property na pocet posidentu - len(self._get_parameters())
        assert len(ctiOS.pocet_expirovanych) == 2
        assert len(ctiOS.pocet_neplatnych) == 1
        assert len(ctiOS.pocet_odstranenych_duplicit) == 1
        assert len(ctiOS.pocet_uspesne_stazenych) == 10

    def test_request_XML(self):
        """Test if created XML from template is not empty and is valid, tag exists."""
        pass

    def test_response_XML(self):
        """Send XML, check http error code, check response XML (not empty, is valid, check nonvalid posidents)"""
        pass

    def test_response_XML_invalid_version(self):
        """Modify request XML (invalid service version), send, check http error code, check response XML"""
        pass
    
    def test_parse_response_XML(self):
        """Parse response XML, check result dictionary"""
        pass

    def test_number_of_keys(self):
        """Check number of keys == 10, check posident codes"""
        pass

    def test_write_output_json(self):
        """Check non empty, is valid, read json, check number of keys, posidents code"""
        pass

    def test_write_output_db(self):
        """Check non empty, is valid, read db, check number of keys, posidents code"""
        pass

    def test_write_output_csv(self):
        """Check non empty, is valid, read csv, check number of keys, posidents code"""
        pass


