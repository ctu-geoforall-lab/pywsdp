# PyWSDP

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
