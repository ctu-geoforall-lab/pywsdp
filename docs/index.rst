========================================================
PyWSDP
========================================================

Open-source knihovna zpřístupňující Webové služby dálkového přístupu do Katastru nemovitostí

Poskytované moduly vycházející z podporovaných WSDP služeb:
 * ČtiOS - zjištění osobních údajů opravněných subjektů z VFK souboru
 * GenerujCernoveUdajeDleKu - vytvoření sestavy pro generování cenových údajů podle katastrálního území  
 * SeznamSestav, VratSestavu, SmazSestavu - spravování sestav

Příklad použití ukázaný na modulu ČtiOS:

.. code-block:: python

    from pywsdp.modules import CtiOS
    
    ucet = ["uzivatel", "heslo"] # platne pristupove udaje k WSDP uctu

    ctios = CtiOS(creds_test) # pripojeni ke sluzbe CtiOS
    
    # pseudonymizovane opravnene subjekty
    identifikatory = ["4m3Yuf1esDMzbgNGYW7kvzjlaZALZ3v3D7cXmxgCcFp0RerVtxqo8yb87oI0FBCtp49AycQ5NNI3vl+b+SEa+8SfmGU4sqBPH2pX/76wyBI",
                      "5wQRil9Nd5KIrn5KWTf8+sksZslnMqy2tveDvYPIsd1cd9qHYs1V9d9uZVwBEVe5Sknvonhh+FDiaYEJa+RdHM3VtvGsIqsc2Hm3mX0xYfs="]

    # poslani pozadavku
    slovnik, slovnik_chybnych = ctios.posli_pozadavek({"pOSIdent": identifikatory})
    
    assert slovnik[identifikatory[0]]['jmeno'] == 'Josef'
    assert slovnik[identifikatory[0]]['prijmeni'] == 'Just'

Úvod
==================

PyWSDP je open-source knihovna vyvíjená na katedře geomatiky fakulty stavební ČVUT. Zpřístupňuje Webové služby dálkového přístupu do Katastru nemovitostí (dále jen WSDP).
Tyto služby poskytované Českým úřadem zeměměřickým a katastrálním jsou programovým rozhraním pro aplikaci Dálkový přístup do KN (DP). Podobně jako DP jsou WSDP služby z větší části placené a využít je mohou pouze registrovaní uživatelé. 

Knihovna PyWSDP poskytuje rozhraní pro práci se dvěma WSDP službami -- samostatně stojící službou Čti OS a službou Generování cenových údajů podle katastrálního území, která je na poli WSDP služeb součástí většího celku s názvem Sestavy.
Pro výše zmíněné dvě služby nabízí knihovna PyWSDP intuitivní rozhraní, které zpracuje XML odpovědi služeb do konkrétních formátů s možností uložení výstupů na disk.

Služba je jednoduše rozšiřitelná o další sestavy i další skupiny služeb jako jsou číselníky, informace, správa účtu a vyhledávání.
Pro rozšíření je nutné doplnit dané službě specifické části kódu pro zpracování odpovědí serveru do požadovaných výstupních formátů.

Instalace
============
Kromě standardtních knihoven používá knihovna PyWSDP pro sestavování SOAP požadavků knihovnu Zeep verze 4.1.0 - https://docs.python-zeep.org/en/master/client.html.
Stažení celé knihovny PyWSDP i s touto závislostí je možné skrze PyPI (https://pypi.org/project/pywsdp/):

Pokud máte nainstalovaný a aktualizovaný pip klient, můžete spustit::

    pip install pywsdp
    
Verze 2.0 podporuje python verze 3.8 a vyšší.


Docker image
============
Repozitář na GitHubu si můžete naklonovat::

    git clone https://github.com/ctu-geoforall-lab/pywsdp.git
    
V naklonovaném adresáři je pak možné si sestavit Docker image. Stačí spustit tento příkaz v rootu adresáře knihovny, kde leží Dockerfile::

    docker build -t pywsdp .
    
Pro otestování knihovny lze připojit testovací skript::

    docker run -it --rm --volume $(pwd)/tests:/tests pywsdp python3 -m pytest /tests/test.py


Průvodce PyWSDP moduly
=========================
Podívejte se na podporované moduly a vyzkoušejte si PyWSDP knihovnu nanečisto skrze testovací účet.

.. toctree::
   :maxdepth: 2

   getting_started
   moduly


Jak moduly použít?
==================
Konkrétní možnosti knihovny jsou názorně ukázany na platformě Jupyter Notebooks:

.. toctree::
   :maxdepth: 2

   notebooks

   
API dokumentace
=================

.. toctree::
   :maxdepth: 2
   
   api



