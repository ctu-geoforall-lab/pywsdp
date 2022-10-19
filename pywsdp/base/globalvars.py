"""
@package base.globals

@brief General global variables

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

# Namespaces
xmlNamespace0 = {
    "sestavy": "{http://katastr.cuzk.cz/sestavy/types/v2.9}",
    "ctios": "{http://katastr.cuzk.cz/ctios/types/v2.8}",
}

xmlNamespace1 = {
    "sestavy": "{http://katastr.cuzk.cz/commonTypes/v2.9}",
    "ctios": "{http://katastr.cuzk.cz/commonTypes/v2.8}",
}

# WSDL endpoints
trialWsdls = {
    "sestavy": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws29/wsdp/sestavy_v29.wsdl",
    "ctios": "https://wsdptrial.cuzk.cz/trial/dokumentace/ws28/ctios/ctios_v28.wsdl",
}

prodWsdls = {
    "sestavy": "https://katastr.cuzk.cz/dokumentace/ws29/wsdp/sestavy_v29.wsdl",
    "ctios": "https://katastr.cuzk.cz/dokumentace/ws28/ctios/ctios_v28.wsdl",
}

# Mapping dictionary for conversion from XML response and DB Gdal SQLITE db
XML2DB_mapping = {
    "priznakKontext": "PRIZNAK_KONTEXTU",
    "partnerBsm1": "ID_JE_1_PARTNER_BSM",
    "partnerBsm2": "ID_JE_2_PARTNER_BSM",
    "charOsType": "CHAROS_KOD",
    "kodAdresnihoMista": "KOD_ADRM",
    "idNadrizenePravnickeOsoby": "ID_NADRIZENE_PO",
}