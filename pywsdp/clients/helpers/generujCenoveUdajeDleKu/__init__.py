"""
@package clients.helpers

@brief Helpers for any Sestavy client

Classes:
 - helpers::ProcessDictionary

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""


class ProcessDictionary:
    """Class processing Sestavy dict response."""

    def __call__(self, input_dict, logger):
        """
        Process dictionary for output.
        Raised:
            WSDPResponseError
        :param input_dict: input dictioonary gained from zeep object
        :param logger: logging class (WSDPLogger)
        :rtype: dict: successfully processed attributes (nested dictonary))
        """
        akce = input_dict["vysledek"]["zprava"][0]["_value_1"]
        logger.info(" ")
        logger.info(akce)
        print(input_dict)
        
        if input_dict["reportList"]:
            report = input_dict["reportList"]["report"][0]
            
            if report["datumPozadavku"]:
                report["datumPozadavku"] = report["datumPozadavku"].strftime("%Y-%m-%dT%H:%M:%S")
            if report["datumSpusteni"]:
                report["datumSpusteni"] = report["datumSpusteni"].strftime("%Y-%m-%dT%H:%M:%S")  
            if report["datumVytvoreni"]:
                report["datumVytvoreni"] = report["datumVytvoreni"].strftime("%Y-%m-%dT%H:%M:%S")  
            return report
        return None