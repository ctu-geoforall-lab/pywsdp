
import os
import json
from pathlib import Path

from pywsdp.services.ctiOS import CtiOSBase
from pywsdp.services.ctiOS.helpers import CtiOSDbManager, CtiOSXml2DbConverter
from pywsdp.services.sestavy import SestavyBase
from pywsdp.base.logger import WSDPLogger
from pywsdp.base.exceptions import WSDPError


class WSDPFactory:
    """Tovarna"""
    def __init__(self):
        self.classes = {}
 
    def register(self, cls):
        self.classes[cls.service_name] = cls
        return cls

    def create(self, recipe, logger):
        """Create service instance based on an input dictionary consisted of
        service name and parameters"""
        if not isinstance(recipe, dict):
            raise WSDPError(
                self.logger,
                "Input is not a dictionary!"
                )
        service_name = list(recipe.keys())[0]
        args = list(recipe.values())[0]
        cls = self.classes[service_name]
        return cls._from_recipe(args, logger)

pywsdp = WSDPFactory()

@pywsdp.register
class GenerujCenoveUdajeDleKu(SestavyBase):
    """
    """
    service_name = "generujCenoveUdajeDleKu"
    logger = WSDPLogger(service_name)

@pywsdp.register
class SeznamSestav(SestavyBase):
    """
    """
    service_name = "seznamSestav"
    logger = WSDPLogger(service_name)

@pywsdp.register
class VratSestavu(SestavyBase):
    """
    """
    service_name = "vratSestavu"
    logger = WSDPLogger(service_name)

@pywsdp.register
class SmazSestavu(SestavyBase):
    """
    """
    service_name = "smazSestavu"
    logger = WSDPLogger(service_name)

@pywsdp.register
class CtiOSDict(CtiOSBase):
    """
    """
    service_name = "ctiOSDict"
    logger = WSDPLogger(service_name)

    @property
    def parameters(self):
        """Method for getting parameters"""
        return self.args["posidents"]

@pywsdp.register
class CtiOSJson(CtiOSBase):
    """
    """
    service_name = "ctiOSJson"
    logger = WSDPLogger(service_name)

    @property
    def parameters(self):
        """Method for getting parameters"""
        json_path = self.args
        file = Path(json_path)
        if file.exists():
            with open(file) as f:
                data = json.load(f)
                return data["posidents"]
        else:
            raise WSDPError(
                self.logger,
                "File is not found!"
                )

@pywsdp.register
class CtiOSDb(CtiOSBase):
    """
    """
    service_name = "ctiOSDb"
    logger = WSDPLogger(service_name)

    def __init__(self):
        super().__init__()
        self.schema = "OPSUB"
        self._mapping_json_path = self._set_mapping_json_path()

    @property
    def mapping_json_path(self):
        """User can get mapping csv to db path"""
        return self._mapping_json_path

    def _set_mapping_json_path(self):
        """
        Set XML template path needed for rendering XML request
        Returns:
            template path (string):  path for rendered XML request
        """
        mapping_json_path = os.path.join(
            self.service_dir,
            "config",
            "attributes_mapping.json",
        )
        return mapping_json_path

    @property
    def parameters(self):
        """Method for getting parameters"""
        sql=None
        if isinstance(self.args, list):
            db_path = self.args[0]
            sql = self.args[1]
        else:
            db_path = self.args

        file = Path(db_path)
        if file.exists():
            db = CtiOSDbManager(db_path, self.logger)
            db._create_connection()
            if sql:
                posidents = db.get_posidents_from_db(sql)
            else:
                posidents = db.get_posidents_from_db()
            db.close_connection()
            return posidents
        else:
            raise WSDPError(
                self.logger,
                "File is not found!"
                )

    def _write_output_to_db(self, result_dict, output_db):
        """Write dictionary to db"""
        file = Path(output_db)
        if file.exists():
            db = CtiOSDbManager(output_db, self.logger)
            db._create_connection()
            db.add_column_to_db(self.schema, "OS_ID", "text")
            columns = db.get_columns_names(self.schema)
            # Convert xml attributes to db
            dictionary = CtiOSXml2DbConverter(
                self.mapping_json_path, self.logger
            ).convert_attributes(columns, result_dict)
            # Save attributes to db
            db.save_attributes_to_db(self.schema, dictionary)
            self.logger.info(
                    "Soubor v ceste {} byl aktualizovan.".format(output_db)
            )
            db.close_connection()
        else:
            raise WSDPError(
                self.logger,
                "File is not found!"
                )
