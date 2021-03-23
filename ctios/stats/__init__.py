###############################################################################
# Name:         CtiOSParser
# Purpose:      Class processing and controlling attributes, it makes statistics
# Date:         March 2021
# Copyright:    (C) 2021 Linda Kladivova
# Email:        l.kladivova@seznam.cz
###############################################################################


class CtiOsStats:
    """
    CTIOS class which read CSV with dictionary of xml tags and database names
    """

    def __init__(self):
        """
        Constructor of CtiOsStats class
        """
        # Statistics
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

