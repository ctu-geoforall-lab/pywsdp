
import os
import json
from pathlib import Path

from services.ctiOS import CtiOSBase
from services.ctiOS.helpers import CtiOSDbManager, CtiOSXml2DbConverter
from services.sestavy import SestavyBase
from base.logger import WSDPLogger
from base.exceptions import WSDPError


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
            self.db_path = db_path
            self.db = CtiOSDbManager(db_path, self.logger)
            self.db._create_connection()
            if sql:
                return self.db.get_posidents_from_db(sql)
            return self.db.get_posidents_from_db()
        else:
            raise WSDPError(
                self.logger,
                "File is not found!"
                )

    def _save_posidents_to_db(self, dictionary):
        """Method for saving posidents to db"""
        self.db.add_column_to_db(self.schema, "OS_ID", "text")
        columns = self.db.get_columns_names(self.schema)
        # Convert xml attributes to db
        dictionary = CtiOSXml2DbConverter(
            self.mapping_json_path, self.logger
        ).convert_attributes(columns, dictionary)
        # Save attributes to db
        self.db.save_attributes_to_db(self.schema, dictionary)
        self.logger.info(
                "Soubor v ceste {} byl aktualizovan.".format(self.db_path)
        )
        self.db.close_connection()

    def _process(self):
        """Main wrapping method"""
        dictionary = super()._process()
        self._save_posidents_to_db(dictionary)
        return dictionary