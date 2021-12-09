
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
        parameters = list(recipe.values())[0]
        cls = self.classes[service_name]
        return cls._from_recipe(parameters, logger)

pywsdp = WSDPFactory()

@pywsdp.register
class GenerujCenoveUdajeDleKu(SestavyBase):
    """A class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    service_name = "generujCenoveUdajeDleKu"
    logger = WSDPLogger(service_name)

@pywsdp.register
class GenerujVystupZeSbirkyListin(SestavyBase):
    """A class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    service_name = "generujVystupZeSbirkyListin"
    logger = WSDPLogger(service_name)

@pywsdp.register
class SeznamSestav(SestavyBase):
    """A class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    service_name = "seznamSestav"
    logger = WSDPLogger(service_name)

@pywsdp.register
class VratSestavu(SestavyBase):
    """A class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    service_name = "vratSestavu"
    logger = WSDPLogger(service_name)

@pywsdp.register
class SmazSestavu(SestavyBase):
    """A class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    service_name = "smazSestavu"
    logger = WSDPLogger(service_name)

@pywsdp.register
class CtiOSDict(CtiOSBase):
    """A class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    service_name = "ctiOSDict"
    logger = WSDPLogger(service_name)

    def _get_parameters(self):
        """Method for getting parameters"""
        return self.parameters["posidents"]

@pywsdp.register
class CtiOSJson(CtiOSBase):
    """A class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    service_name = "ctiOSJson"
    logger = WSDPLogger(service_name)

    def _get_parameters(self):
        """Method for getting parameters"""
        json_path = self.parameters
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
    """A class that defines interface and main logic used for generujCenoveUdajeDleKu service.

    Several methods has to be overridden or
    NotImplementedError(self.__class__.__name__+ "MethodName") will be raised.
    """

    schema = "OPSUB"
    service_name = "ctiOSDb"
    logger = WSDPLogger(service_name)

    def __init__(self):
        super().__init__()
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

    def _get_parameters(self):
        """Method for getting parameters"""
        sql=None
        if isinstance(self.parameters, list):
            db_path = self.parameters[0]
            sql = self.parameters[1]
        else:
            db_path = self.parameters

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
