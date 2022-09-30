from zeep import Client, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken

import sys

trialWsdls = {
    "sestavy": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/sestavy_v29.wsdl",
    "ciselnik": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/ciselnik_v29.wsdl",
    "vyhledat": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/vyhledat_v29.wsdl",
    "informace": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/informace_v29.wsdl",
    "ucet": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/ucet_v29.wsdl",
    "ctios": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws28/ctios/ctios_v28.wsdl",  
}

prodWsdls = {
    "sestavy": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/sestavy_v29.wsdl",
    "ciselnik": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/ciselnik_v29.wsdl",
    "vyhledat": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/vyhledat_v29.wsdl",
    "informace": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/informace_v29.wsdl",
    "ucet": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/ucet_v29.wsdl",
    "ctios": "https://katastr.cuzk.cz/dokumentace/ws28/ctios/ctios_v28.wsdl",
}

transport = Transport(cache=SqliteCache())
settings = Settings(raw_response=False, strict=False, xml_huge_tree=True)
settings = Settings(strict=False, xml_huge_tree=True)


class WSDPBase:
	
	@classmethod
	def _from_recipe(cls, wsdl, service_name, creds, trial=False):
		result = cls()
		if trial == True:
			result.client = Client(trialWsdls[wsdl],
								transport=transport,
								wsse=UsernameToken(*creds),
								settings=settings,
							)
		else:
			result.client = Client(prodWsdls[wsdl],
								transport=transport,
								wsse=UsernameToken(*creds),
								settings=settings,
							)			
		result.service_name = service_name
		result.creds = creds
		return result


class WSDPFactory:
	
	def __init__(self):
		self.classes = {}
	
	def register(self, cls):
		self.classes[cls.service_name] = cls
		return cls
	
	def create(self, *args, **kwargs):
		if args[1]:
			service_name = args[1]
		cls = self.classes[service_name]
		return cls._from_recipe(*args, **kwargs)
		

pywsdp = WSDPFactory()


@pywsdp.register
class CtiOs(WSDPBase):
	
	service_name = "ctios"
	
	def zpracuj_identifikatory(self, pOSIdent):
		return self.client.service.ctios(pOSIdent=pOSIdent)

	
def WSDPClient(wsdl, service_name, creds, trial=False):
	return pywsdp.create(wsdl, service_name, creds, trial=trial)

		
if __name__ == "__main__":

	creds_test = ["WSTEST", "WSHESLO"]

	pywsdp_client = WSDPClient("ctios", "ctios", creds_test, trial=True)
	print(pywsdp_client.zpracuj_identifikatory(pOSIdent="m+o3Qoxrit4ZwyJIPjx3X788EOgtJieiZYw/eqwxTPERjsqLramxBhGoAaAnooYAliQoVBYy7Q7fN2cVAxsAoUoPFaReqsfYWOZJjMBj/6Q="))
		
