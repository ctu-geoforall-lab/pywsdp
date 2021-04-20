"""
@package pywsdp.base

@brief Base script for general classes needed for WSDP services

Classes:
 - base::WSDPTemplate

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""

import os
from string import Template


class WSDPTemplate():
    """
    WSDPTemplate class reads XML template and prepare it for given service
    """

    def __init__(self, template_dir=None):
        """
        Constructor of Templates class

        Args:
          template_dir (str): Template directory has to be absolute path, relative paths are not supported
        """
        if template_dir and os.path.isabs(template_dir):
            self.template_dir = template_dir
        else:
            self.template_dir = os.path.join(
                os.path.dirname(__file__)
            )

    def _read_template(self, template_name):
        """
        Read template

        Args:
            template_name (str): name of template xml file

        Returns:
            template.read()
        """
        with open(os.path.join(self.template_dir, template_name)) as template:
            return template.read()

    def render(self, template_name, **kwargs):
        """
        Render template using arguments

        Args:
            template_name (str): name of template xml file
            **kwargs: keyword arguments

        Returns:
            Template()
        """
        return Template(
            self._read_template(template_name)
        ).substitute(**kwargs)