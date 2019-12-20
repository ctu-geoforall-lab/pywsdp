import csv
import os


class CtiOsCsv:
    """
    CTIOS class which read CSV with dictionary of xml tags and database names
    """

    def __init__(self, csv_dir):
        """
        Constructor of CtiOsCsv class

        Args:
          csv_dir (str): Csv directory has to be absolute path, relative paths are not supported
        """
        if csv_dir and os.path.isabs(csv_dir):
            self.csv_dir = csv_dir
        else:
            # relative paths are not supported
            self.csv_dir = os.path.join(
                os.path.dirname(__file__)
            )

    def read_csv_as_dictionary(self, csv_name):
        """
        Read csv attributes as dictionary

        Args:
            csv_name (str): name of attribute mapping csv file

        Returns:
            dictionary (dict): (1.column:2.column)
        """
        dictionary = {}
        with open(os.path.join(self.csv_dir, csv_name)) as csv_file:
            rows = csv.reader(csv_file, delimiter=';')
            for row in rows:
                [k, v, l] = row
                dictionary[k] = v
            return dictionary
