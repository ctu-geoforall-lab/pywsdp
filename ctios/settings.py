from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR.joinpath('templates')
CSV_DIR = BASE_DIR.joinpath('csv')
ATTRIB_MAP_FILE = 'attributes_mapping.csv'
