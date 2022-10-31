"""
@package base.logger

@brief General logging class for WSDP services

Classes:
 - base::WSDPLogger

(C) 2021 Linda Kladivova lindakladivova@gmail.com
This library is free under the MIT License.
"""

import logging
from datetime import datetime


class WSDPLogger(logging.getLoggerClass()):
    """
    General WSDP class for logging
    """

    def __init__(self, name: str, level=logging.ERROR):
        """
        Contructor of WSDPLogger class, format console handler
        :param name: service name (str)
        :param level: logging level ()
        """
        super().__init__(name)

        # Define a level of log messages
        logging.basicConfig(level=level)

        # Define a Stream Console Handler
        console = logging.StreamHandler()

        # Create formats and add it to console handler
        formatter = logging.Formatter("%(name)-12s - %(levelname)-8s - %(message)s")
        console.setFormatter(formatter)

        # Add handlers to the logger
        self.addHandler(console)

    def set_directory(self, log_dir: dir):
        """
        Set log directory
        :param log_dir: path to log directory (str)
        """

        log_filename = datetime.now().strftime("%H_%M_%S_%d_%m_%Y.log")

        file_handler = logging.FileHandler(
            filename=log_dir + "/" + log_filename, mode="w"
        )

        formatter = logging.Formatter(
            "%(name)-12s %(asctime)s %(levelname)-8s %(message)s"
        )
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.addHandler(file_handler)

    def __del__(self):
        logging.shutdown()
