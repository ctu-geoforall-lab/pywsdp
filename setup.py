import setuptools
from pywsdp import __version__
from pathlib import Path

root_dir = Path(__file__).parent

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pywsdp",
    version=__version__,
    author="Linda Kladivova",
    author_email="lindakladivova@gmail.com",
    description="PyWSDP Python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ctu-geoforall-lab/pywsdp",
    packages=setuptools.find_packages(),
    scripts=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "zeep>=4.1.0",
    ],
)
