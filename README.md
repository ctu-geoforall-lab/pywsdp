# PyWSDP - Python knihovna zpřístupňující webové služby dálkového přístupu do KN

[![pytest](https://github.com/ctu-geoforall-lab/pywsdp/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/ctu-geoforall-lab/pywsdp/actions/workflows/pytest.yml)
[![PyPI Latest Release](https://img.shields.io/pypi/v/pywsdp.svg)](https://pypi.org/project/pywsdp/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## O co se jedná?
**PyWSDP** nabízí rozhraní pro komunikaci s webovými službami dálkového přístupu do KN (WSDP).
V poslední verzi nabízí podporu dvou služeb - ČtiOS a Generování cenových údaje podle katastrálního území.
Kromě intuitivního dotazování nabízí možnosti čtení a zápisu do několika formátů.

## Instalace PyWSDP
PyWSDP je k dispozici ke stažení na PyPI:

```console
$ python -m pip install pywsdp
```

## Dokumentace
Podrobná dokumentace s ukázkovými příklady použití je zde:

https://ctu-geoforall-lab.github.io/pywsdp/

## Docker
Sestavte si Docker image ze staženého zdrojového kodu (sestavení je třeba spustit v kořenovém adresáři knihovny):

```
docker build -t pywsdp .
```

Sestavený image můžeme otestovat vytvořením testovacího kontejneru:

```
docker run -it --rm --volume $(pwd)/tests:/tests pywsdp python3 -m pytest /tests/test.py
```
