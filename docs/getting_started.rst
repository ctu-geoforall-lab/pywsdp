========================================================
Testovací prostředí
========================================================

SOAP služby WSDP je možné skrze PyWSDP knihovnu ozkoušet dotazováním se na tzv. služby "na zkoušku".
Pro tyto služby jsou uvnitř PyWSDP knihovny uloženy upravené URL adresy. Zdrojem dat je databáze DP, nicméně vrácená data jsou omezeného rozsahu.
Jejich obsahová stránka byla pozměněna tak, aby neodpovídala platnému stavu KN.

Služby na zkoušku je možné vyzkoušet skrze speciální aplikační účet (uživatel WSTEST a heslo WSHESLO) ,
který simuluje přístup běžného platícího uživatele.

Pro osahání API doporučujeme si obě služby nejprve vyzkoušet pod testovacím účtem.
Při vytváření instance modulu je nutné nastavit parametr trial=True.

Modul CtiOS:

.. code-block:: python

    from pywsdp.modules import CtiOS
    
    ucet = ["WSTEST", "WSHESLO"] # pristupove udaje

    ctios = CtiOS(ucet, trial=True) # pripojeni k CtiOS
    
Podobně pro modul GenerujCenoveUdajeDleKu:

.. code-block:: python

    from pywsdp.modules import GenerujCenoveUdajeDleKu
    
    ucet = ["WSTEST", "WSHESLO"]

    cen_udaje = GenerujCenoveUdajeDleKu(ucet, trial=True)