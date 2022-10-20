"""
@package clients.helpers

@brief Helpers for CtiOS client

Classes:
 - helpers::ProcessDictionary
 - helpers::Counter

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""


class ProcessDictionary:
    """Class processing ctiOS dict response."""

    def __call__(self, input_dict, counter, logger):
        """
        Process dictionary for output.
        Raised:
            WSDPResponseError
        :param input_dict: input dictioonary gained from zeep object
        :param counter: counts posident errors (Counter class)
        :param logger: logging class (WSDPLogger)
        :rtype: tuple (successfully processed attributes (nested dictonary), errors (dictionary))
        """
        akce = input_dict["vysledek"]["zprava"][0]["_value_1"]
        logger.info(" ")
        logger.info(akce)

        dictionary = {}
        dictionary_errors = {}
        posident_list = input_dict["osList"]["os"]

        for identifikator in posident_list:
            posident = identifikator["pOSIdent"]
            if identifikator["chybaPOSIdent"]:
                chyba_posident = identifikator["chybaPOSIdent"]
                if chyba_posident == "NEPLATNY_IDENTIFIKATOR":
                    counter.add_neplatny_identifikator()
                elif chyba_posident == "EXPIROVANY_IDENTIFIKATOR":
                    counter.add_expirovany_identifikator()
                elif chyba_posident == "OPRAVNENY_SUBJEKT_NEEXISTUJE":
                    counter.add_opravneny_subjekt_neexistuje()
                logger.info(
                    "POSIDENT {} {}".format(posident, chyba_posident.replace("_", " "))
                )
                dictionary_errors[posident] = chyba_posident
            else:
                os_detail = identifikator["osDetail"][0]
                os_detail["osId"] = identifikator["osId"]
                if os_detail["datumVzniku"]:
                    os_detail["datumVzniku"] = os_detail["datumVzniku"].strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )
                if os_detail["datumZaniku"]:
                    os_detail["datumZaniku"] = os_detail["datumZaniku"].strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )
                counter.add_uspesne_stazeno()
                logger.info("POSIDENT {} USPESNE STAZEN".format(posident))
                dictionary[posident] = os_detail
        return dictionary, dictionary_errors


class Counter:
    """
    Counts posident stats.
    """

    def __init__(self):
        """
        Initialize posidents stats.
        """
        self.neplatny_identifikator = 0
        self.expirovany_identifikator = 0
        self.opravneny_subjekt_neexistuje = 0
        self.uspesne_stazeno = 0

    def add_neplatny_identifikator(self):
        self.neplatny_identifikator += 1

    def add_expirovany_identifikator(self):
        self.expirovany_identifikator += 1

    def add_opravneny_subjekt_neexistuje(self):
        self.opravneny_subjekt_neexistuje += 1

    def add_uspesne_stazeno(self):
        self.uspesne_stazeno += 1
