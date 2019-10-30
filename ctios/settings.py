from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR.joinpath('templates')
CSV_DIR = BASE_DIR.joinpath('csv')
