#!/usr/bin/env python3

from zeep import Client, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken

TRIAL = True

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
    "ctios": "https://katastr.cuzk.cz/dokumentace/ws28/wsdp/ctios_v28.wsdl",
}

creds_test = ["WSTEST", "WSHESLO"]
creds_overujici = ["WSTESTO", "WSHESLOO"]
creds_bezuplatny = ["WSTESTB", "WSHESLOB"]

def PyWSDPClient(wsdl, creds):
    transport = Transport(cache=SqliteCache())
    settings = Settings(raw_response=False, strict=False, xml_huge_tree=True)
    settings = Settings(strict=False, xml_huge_tree=True)
    relevantWsdls = prodWsdls
    if TRIAL:
        relevantWsdls = trialWsdls
        
    return Client(relevantWsdls[wsdl],
        transport=transport,
        wsse=UsernameToken(*creds),
        settings=settings,
    )


if __name__ == "__main__":
    print(PyWSDPClient("informace", creds_bezuplatny).service.dejNahledLV(
        katuzeKod=693936,
        lvCislo=310
    ))

    print(PyWSDPClient("informace", creds_test).service.dejMBRParcel(
        parcelaId=2850900306,
    ))
    
    print(PyWSDPClient("sestavy", creds_test).service.generujLVZjednodusene(
        lvCislo=310,
        katastrUzemiKod=693936,
        format='xml',
    ))
