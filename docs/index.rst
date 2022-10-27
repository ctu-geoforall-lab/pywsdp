========================================================
PyWSDP
========================================================

Open-source knihovna zpřístupňující Webové služby dálkového přístupu do Katastru nemovitostí

Podporované služby s možností několika vstupních a výstupních formátů:
 * Čti OS - zjištění osobních údajů opravněných subjektů z VFK souboru
 * Sestava pro generování cenových údajů dle katastrálních území  

Příklad použití:

.. code-block:: python

    print("TBD")

Úvod
==================

PyWSDP je open-source knihovna vyvíjená na katedře geomatiky fakulty stavební ČVUT. Zpřístupňuje Webové služby dálkového přístupu do Katastru nemovitostí (dále jen WSDP).
Tyto služby poskytované Českým úřadem zeměměřickým a katastrálním jsou programovým rozhraním pro aplikaci Dálkový přístup do KN (DP). Podobně jako DP jsou WSDP služby z větší části placené a využít je mohou pouze registrovaní uživatelé. 

Knihovna PyWSDP poskytuje rozhraní pro práci se dvěma WSDP službami -- samostatně stojící službou Čti OS a službou Generování cenových údajů dle katastrálních území, která je na poli WSDP služeb součástí většího celku s názvem Sestavy.
Pro výše zmíněné dvě služby nabízí knihovna PyWSDP výstup do několika formatů, které jsou popsány v dokumentaci.

Služba je jednoduše rozšiřitelná o další sestavy. Pro rozšíření je nutné doplnit dané službě specifické XML konvertory pro výstupy do požadovaných výstupních formátů.
Konvertory a SOAP komunikace s WSDP službami společně tvoří API jednotlivých PyWSDP služeb.

Instalace
============
Kromě standardtních knihoven používá knihovna PyWSDP pro sestavování SOAP požadavků knihovnu Zeep verze 4.1.0 - https://docs.python-zeep.org/en/master/client.html.
Stažení celé knihovny PyWSDP i s touto závislostí je možné skrze PyPI (https://pypi.org/project/pywsdp/):

Pokud máte nainstalovaný a aktualizovaný pip klient, můžete spustit::

    pip install pywsdp
    
Verze 1.1 podporuje python verze 3.8 a vyšší.


Docker image
============
Repozitář na GitHubu si můžete naklonovat::

    git clone https://github.com/ctu-geoforall-lab/pywsdp.git
    
V naklonovaném adresáři je pak možné si sestavit Docker image. Stačí spustit tento příkaz v rootu adresáře knihovny, kde leží Dockerfile::

    docker build -t pywsdp .
    
Pro otestování knihovny lze připojit testovací skript::

    docker run -it --rm --volume $(pwd)/tests:/tests pywsdp python3 -m pytest /tests/test.py


Průvodce PyWSDP službami
=========================

.. toctree::
   :maxdepth: 2

   getting_started
   ctios
   sestavy

   
API dokumentace
=================
.. toctree::
   :maxdepth: 2

   api


Jupyter notebooky
=================
.. toctree::
   :maxdepth: 2

   notebooks



