##############################################################
Poskytované moduly
##############################################################

Knihovna poskytuje rozhraní ve formě modulů pro tyto WSDP služby:
 * ctiOS - zjištění osobních údajů opravněných subjektů z VFK souboru
 * generujCernoveUdajeDleKu - vytvoření sestavy pro generování cenových údajů dle katastrálních území  
 * seznamSestav, vratSestavu, smazSestavu - spravování sestav
 
Jednotlivé moduly budou na dalších řádcích podrobněji popsány.
Konkrétní obsah výstupních dat WSDP je možné dohledat na stránkách ČÚZK -
https://www.cuzk.cz/Katastr-nemovitosti/Poskytovani-udaju-z-KN/Dalkovy-pristup/Webove-sluzby-dalkoveho-pristupu.aspx .

ČtiOS
######
Rozhraní umožňuje získat a uložit v různých formátech osobní údaje k oprávněným subjektům (OS), které byly pseudonymizovány ve VFK souboru v souvislosti s nařízením GDPR.
Dešifrování pseudonymizovaných identifikatorů oprávněných subjektů (tzv. POSIdentů) a zjišťování jejich osobních údajů není programovou součástí této knihovny.
Knihovna přistupuje k WSDP službě ctiOS, která se stará o tuto "špinavou práci". Na straně ČÚZK je přístup ke službě ctiOS monitorován ukládáním záznamů o všech vyhledaných OS.

Modul ČtiOS získává výstup ze serveru ve formě slovníků, které dále připraví pro uložení do souborů vybraných formátů.
Při uložení úspěšně zpracovaných identifikátorů do souboru o vybraném výstupním formátu se automaticky ve stejné složce vytvoří JSON soubor obsahující neúspěšně zpracované
identifikátory a odůvodnění.

Důvody neúspěšného zpracování POSIdentů vychází z nastavení služby ctiOS a jsou následující:
 - NEPLATNY_IDENTIFIKATOR - každý POSIdent, který nebylo možné rozšifrovat
 - EXPIROVANY_IDENTIFIKATOR - POSIdent, kterému vypršela časová platnost
 - OPRAVNENY_SUBJEKT_NEEXISTUJE - POSIdent bylo možné rozšifrovat, ale oprávněný subjekt k němu neexistuje

Vstupní formáty
------------------
Rozhraní umožňuje načítat data z SQLite databáze či JSON souboru. Dále umožňuje vstupní POSIdenty zadat i přímo jako slovník do volání služby.

Pokud chceme pracovat s daty z VFK souboru, je pro nás určeno načítání vstupních dat z SQLite databáze.
Tuto databázi musíme nejprve z VFK souboru vytvořit pomocí nástroje **ogrinfo**, který je součástí knihovny GDAL::

    ogrinfo exportvse.vfk

Tento driver vytvoří SQLite databázi ve stejném adresáři jako VFK soubor s příponou .db. To lze ověřit například pomocí aplikace SQLite Database Browser.

Výstupní formáty
------------------
Získaná data oprávněných subjektů je možné uložit do tří formátů - JSON, CSV a SQlite databáze.
V případě SQLite databáze je nutné mít i vstupní data ve formě SQLite databáze.
Na základě vstupní databáze modul vytvoří ve zvolené cestě novou databázi s updatovanými atributy oprávněných subjektů.


Sestavy
#######################


GenerujCenoveUdajeDleKu
------------------------

Rozhraní umožňuje práci se sestavou na generování údajů o dosažených cenách nemovitostí podle zadaného kódu k.ú. pro dané časové období.
Po dotazu na server modul vytvoří sestavu, se kterou je poté možné přes rozhraní dále pracovat - vypsat údaje o sestavě (cena, stav sestavy apod.), zaúčtovat sestavu a smazat sestavu.

Můžeme načítat vstupní data ze souboru JSON nebo je zadat přímo jako slovník do volání služby.

Výstupní ZIP soubor obsahuje XML soubory s cenovými údaji pro dané časové období.
Po zaúčtování je možné zašifrovaný ZIP dokument pomocí modulu dešifrovat a uložit na disk.

Spravování sestav
#######################
Jedná se o specifické moduly, které je možné využívat v rámci API sestav.
Kromě toho knihovna PyWSDP nabízí i samostatné moduly pro tyto specifické služby.
Pokud znáte číslo sestavy, je možné nad takovou sestavou i samostatně zavolat požadovaný modul.

SeznamSestav vrací údaje o sestavě - typu sestavy, ceně, stavu sestavy
a informace o tom, zda je sestava opatřena el. značkou.

VratSestavu zaúčtuje sestavu (pokud ještě nebyla zaúčtována) a vrátí vygenerovanou sestavu jako součást odpovědi.
Dále vrátí informace o typu sestavy, ceně, stavu sestavy a informaci o tom, zda je
sestava opatřena el. značkou.

SmazSestavu smaže požadovanou sestavu, tzn. k sestavě již nebude možné přistupovat.
