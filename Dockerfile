FROM python:3.10-slim-bullseye

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

COPY pywsdp/ ./pywsdp
COPY setup.py .
COPY README.md .

RUN pip install .
