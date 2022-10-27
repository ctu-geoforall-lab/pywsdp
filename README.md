# PyWSDP

[![pytest](https://github.com/ctu-geoforall-lab/pywsdp/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/ctu-geoforall-lab/pywsdp/actions/workflows/pytest.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python CUZK WSDP Library

Library for communication with WSDP CUZK services.

## Installing PyWSDP

PyWSDP is available on PyPI:

```console
$ python -m pip install pywsdp
```

## Documentation

https://ctu-geoforall-lab.github.io/pywsdp/

## Docker

Build a docker image using the downloaded source code (run this in the directory
containing the source code):

```
docker build -t pywsdp .
```

A test run

```
# launching in tests from tests/ directory:
docker run -it --rm --volume $(pwd)/tests:/tests pywsdp python3 -m pytest /tests/test.py
```
