import os
from string import Template


class CtiOsTemplate:
    def __init__(self, TEMPLATE_DIR):
        if TEMPLATE_DIR and os.path.isabs(TEMPLATE_DIR):
            self.TEMPLATE_DIR = TEMPLATE_DIR
        else:
            # relative paths are not supported
            self.TEMPLATE_DIR = os.path.join(
                os.path.dirname(__file__)
            )

    def _read_template(self, template_name):
        with open(os.path.join(self.TEMPLATE_DIR, template_name)) as template:
            return template.read()

    def render(self, template_name, **kwargs):
        return Template(
            self._read_template(template_name)
        ).substitute(**kwargs)
