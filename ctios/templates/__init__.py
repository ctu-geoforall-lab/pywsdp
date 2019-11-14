import os
from string import Template

class CtiOsTemplate:
    def __init__(self, TEMPLATES_DIR):
        self.TEMPLATES_DIR = TEMPLATES_DIR

    def _read_template(self, template_path):
        with open(os.path.join(self.TEMPLATES_DIR, template_path)) as template:
            return template.read()

    def render(self, template_path, **kwargs):
        return Template(
            self._read_template(template_path)
        ).substitute(**kwargs)
