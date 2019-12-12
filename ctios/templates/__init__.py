import os
from string import Template

class CtiOsTemplate:
    def __init__(self, TEMPLATES_DIR):
        if TEMPLATES_DIR and os.path.isabs(TEMPLATES_DIR):
            self.TEMPLATES_DIR = TEMPLATES_DIR
        else:
            # relative paths are not supported
            self.TEMPLATES_DIR = os.path.join(
                os.path.dirname(__file__)
            )

    def _read_template(self, template_path):
        with open(os.path.join(self.TEMPLATES_DIR, template_path)) as template:
            return template.read()

    def render(self, template_path, **kwargs):
        return Template(
            self._read_template(template_path)
        ).substitute(**kwargs)
