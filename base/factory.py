import os
import json
from datetime import datetime
from pathlib import Path
from services.sestavy import SestavyBase
from base.logger import WSDPLogger


class WSDPFactory:
    """tovarna"""
    def __init__(self):
        self.classes = {}
 
    def register(self, cls):
        self.classes[cls.service_name] = cls
        return cls
 
    def create(self, recipe):
        "Dictionary or json file"
        if isinstance(recipe, dict):
            data = recipe
        else:
            file = Path(recipe)
            if file.exists():
                with open(file) as f:
                    data = json.load(f)
        service_name = list(data.keys())[0]
        parameters = list(data.values())[0]
        cls = self.classes[service_name]
        return cls._from_recipe(parameters)


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


class GenerujCenoveUdajeDleKuFacade():

    def __init__(self):
        self.cen_udaje = None
        self.seznam_sestav = None
        self.vrat_sestavu = None
        self.smaz_sestavu = None

    @property
    def credentials(self):
        """User can get log dir"""
        return (self.cen_udaje.username, self.cen_udaje.password)

    @credentials.setter
    def credentials(self, username, password):
        """User sets his WSDP username and password"""
        self.cen_udaje.username = username
        self.cen_udaje.password = password

    def get_parameters_from_json(self, json):
        self.cen_udaje = pywsdp.create(json)

    def get_parameters_from_dict(self, dictionary):
        self.cen_udaje = pywsdp.create(dictionary)

    def vytvorSestavu(self):
        self.cen_udaje.process()

    def ziskejInfoOSestave(self):
        self.parameters = {'seznamSestav': {'idSestavy': self.get_listina_id()}}
        seznam_sestav = pywsdp.create(self.parameters)
        seznam_sestav.credentials(username=self.cen_udaje.username,
                                  password=self.cen_udaje.password)
        seznam_sestav.process()

    def zauctujSestavu(self):
        self.parameters = {'vratSestavu': {'idSestavy': self.get_listina_id()}}
        vrat_sestavu = pywsdp.create(self.parameters)
        vrat_sestavu.set_credentials(username=self.cen_udaje.username,
                                     password=self.cen_udaje.password)
        vrat_sestavu.process()

    def smazSestavu(self):
        self.parameters = {'smazSestavu': {'idSestavy': self.get_listina_id()}}
        smaz_sestavu = pywsdp.create(self.parameters)
        smaz_sestavu.set_credentials(username=self.cen_udaje.username,
                                     password=self.cen_udaje.password)
        smaz_sestavu.process()
        self.not_deleted = False

    def get_listina_id(self):
        """Main wrapping method"""
        return self.cen_udaje.result_dict["idSestavy"]

    def get_format(self):
        """Main wrapping method"""
        return self.cen_udaje.result_dict["format"]

    def get_soubor_sestavy(self):
        """Main wrapping method"""
        return self.vrat_sestavu.result_dict["souborSestavy"]

    def write_output(self, output_dir=None):
        """Decode base64 string and write output to out dir"""
        import base64
        binary = base64.b64decode(self.get_soubor_sestavy())
        date = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
        output_file = "cen_udaje_{}.{}".format(date, self.get_format())
        with open(os.path.join(output_dir, output_file), 'wb') as f:
            f.write(binary)

    def __del__(self):
        if self.not_deleted:
            self.smazSestavu()


