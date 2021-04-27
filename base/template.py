"""
@package base.template

@brief Base script for general classes needed for WSDP services

Classes:
 - base::WSDPTemplate

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the GNU General Public License.
"""

from string import Template


class WSDPTemplate():
    """
    WSDPTemplate class reads XML template and prepare it for given service
    """

    def __init__(self, template_path):
        """
        Constructor of Templates class

        Args:
          template_path (str): path to template XML file
        """
        self.template_path = template_path

    def _read_template(self):
        """
        Read template

        Args:
            template_name (str): name of template xml file

        Returns:
            template.read()
        """
        with open(self.template_path) as template:
            return template.read()

    def render(self,  **kwargs):
        """
        Render template using arguments

        Args:
            template_name (str): path to template XML file
            **kwargs: keyword arguments

        Returns:
            Template()
        """
        return Template(self._read_template()).substitute(**kwargs)