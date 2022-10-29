========================================================
Veřejné API
========================================================

.. module:: pywsdp

Veřejné API knihovny tvoří moduly.
Ty umožňují intuitivní dotazování vybraných WSDP služeb a ukládání odpovědí do různých formátů.

.. automodule:: pywsdp.modules
   :members:

Společné API pro všechny moduly
========================================================

.. autoclass:: pywsdp.base.WSDPBase
   :members:


Společné API pro hlavní moduly typu sestava
========================================================

.. autoclass:: pywsdp.base.SestavyBase
   :members:
   :show-inheritance:
   

API k hlavním modulům
========================================================

Čti OS
---------

.. autoclass:: pywsdp.modules.CtiOS
   :members:
   :show-inheritance:


Generuj cenové údaje dle katastrálních území
-----------------------------------------------

.. autoclass:: pywsdp.modules.GenerujCenoveUdajeDleKu
   :members:
   :show-inheritance:
   

API k modulům na správu sestav
========================================================
   
Seznam Sestav
-----------------------------------------------

.. autoclass:: pywsdp.modules.SeznamSestav
   :members:
   :show-inheritance:
   

Vrácení sestavy
-----------------------------------------------

.. autoclass:: pywsdp.modules.VratSestavu
   :members:
   :show-inheritance:
   

Smazání sestavy
-----------------------------------------------

.. autoclass:: pywsdp.modules.SmazSestavu
   :members:
   :show-inheritance:
