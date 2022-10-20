"""
@package modules.GenerujCenoveUdajeDleKu

@brief Public API for GenerujCenoveUdajeDleKu module

Classes:
 - GenerujCenoveUdajeDleKu::GenerujCenoveUdajeDleKU

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import os
import base64
from datetime import datetime

from pywsdp.base import SestavyBase


class GenerujCenoveUdajeDleKu(SestavyBase):
    """Trida definujici rozhrani pro praci se sluzbou Generuj cenove udaje dle katastralnich uzemi.

    :param creds:
    :param trial:
    """

    def __init__(self, creds: dict, trial: dict = False):
        self._nazev_sluzby = "generujCenoveUdajeDleKu"

        super().__init__(creds, trial=trial)

    def uloz_vystup(self, zauctovana_sestava: dict, vystupni_adresar: str) -> str:
        """Rozkoduje soubor z vystupnich hodnot sluzby VratSestavu a ulozi ho na disk.

        :param zauctovana_sestava: slovnik vraceny po zauctovani sestavy
        :rtype: string - cesta k vystupnimu souboru
        """
        datum = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
        vystupni_soubor = "cen_udaje_{}.{}".format(datum, zauctovana_sestava["format"])
        vystupni_cesta = os.path.join(vystupni_adresar, vystupni_soubor)
        binary = base64.b64decode(zauctovana_sestava["souborSestavy"])
        with open(vystupni_cesta, "wb") as f:
            f.write(binary)
            self.logger.info(
                "Vystupni soubor je k dispozici zde: {}".format(vystupni_cesta)
            )
        return vystupni_cesta
