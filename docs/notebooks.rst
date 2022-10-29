##################
Jupyter notebooky
##################

Na následujících řádcích si ukážeme příklady použití jednotlivých modulů pomocí nástroje Jupyter Notebooks,
který nám zpřístupní interaktivní prostředí založené na použití webového rozhraní.

ČtiOS
######
Pro tento modul máme připraveny dva Jupyter sešity.

První se věnuje nejčastějšímu případu, kdy máme na vstupu SQLite databázi obsahující data VFK.
Osobní data jako jméno, příjmení apod. zde nejsou vyplněna. Co je ovšem součástí databáze (konkrétně tabulky OPSUB) jsou tzv. pseudonymizované identifikátory OS,
které jsou určeny pro rozklíčování pravých OS a jejich osobních údajů. Modul ČtiOS data rozklíčuje a novou "doplněnou" databázi uloží do námi zvoleného adresáře.
Rozklíčená data můžeme uložit i do CSV nebo JSON souboru, jako je ukázáno v druhém sešitu.

.. toctree::
   
   notebooks/ctios_db
   notebooks/ctios_json_csv
   
Sestavy
#######################
Pro sestavy máme připravenu ukázku použití modulu GenerujCenoveUdajeDleKu s využitím veřejného API sestav,
které využívá WSDP služby seznamSestav, vratSestavu a smazSestavu.
Modul umí na základě vstupního JSON souboru vytvořit sestavu, zaúčtovat sestavu a smazat sestavu z účtu.
Dále modul umožňuje dešifrovat soubor sestavy formátu ZIP a uložit do do námi zvoleného adresáře.

GenerujCenoveUdajeDleKu
------------------------

.. toctree::
   
   notebooks/cenove_udaje_dle_ku_json_zip
   
Spravování sestav
#######################
Na příkladu modulu GenerujCenoveUdajeDleKu si ukážeme, že můžeme získávat info o sestávách, zaúčtovávat sestavy a mazat sestavy i pomocí samostatných modulů.

.. toctree::
   
   notebooks/spravuj_sestavy
