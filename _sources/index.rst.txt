========================================================
Dokumentace k PyWSDP
========================================================
   
PYWSDP je open-source knihovna zpřístupňující **Webové služby dálkového přístupu do Katastru nemovisti (dále jen WSDP)**.
Tyto služby poskytované Českým úřadem zeměměřickým a katastrálním jsou programovým rozhraním pro aplikaci Dálkový přístup do KN (DP). Podobně jako DP jsou WSDP služby z větší části placené a využít je mohou pouze registrovaní uživatelé. 
Knihovna poskytuje rozhraní pro práci se dvěma WSDP službami -- **Čti OS** a **Generování cenových údajů dle katastrálních území**.
Nabízí výstup do několika formatů, které jsou popsány v dokumentaci.

Seznam modulů
========================================================

Čti OS
.......
Rozhraní umožňuje doplnit do vstupního VFK souboru osobní údaje k opravněným subjektům.

* **Input formats:** JSON, TXT, Sqlite databáze (možnost omezení konkrétních pseudoidentifikátorů přes SQL dotaz), Python slovník

* **Output formats:** JSON, CSV, updatovaná Sqlite databáze


Generování cenových údajů dle k. ú.
..................................................
Rozhraní umožňuje práci se sestavami, konkrétně se sestavou na generování cenových údajů dle KÚ pro zadaná čtvrtletí.

* **Input formats:** JSON, TXT, Python slovník

* **Output formats:** ZIP soubor obsahující XML pro zadané měsíce


Jak moduly použít?
===========================
Vyzkoušejte interaktivní jupyter notebooky, kde je práce s jednotlivými moduly podrobněji vysvětlena.

.. toctree::
   :maxdepth: 2

   notebooks/CtiOS
   
.. toctree::
   :maxdepth: 1

   notebooks/GenerujCenoveUdajeDleKu

Podrobnější informace o této aplikaci, poskytovaných výstupech a technických předpokladech použití aplikace naleznete  v "Popisu knihovny PYWSDP". Zájemci se s touto knihovnou a službami WSDP mohou seznámit bezplatně prostřednictví zákaznického účtu „na zkoušku“.



