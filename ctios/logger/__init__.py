import logging
from datetime import datetime
import os

class CtiOsLogger(logging.getLoggerClass()):
    def __init__(self, name='pyctios', level=logging.DEBUG):
        super(CtiOsLogger, self).__init__(name)

        self.setLevel(level)

        # Define a Stream Console Handler
        console = logging.StreamHandler()

        # Create formats and add it to console handler
        formatter = logging.Formatter('%(name)-12s - %(levelname)-8s - %(message)s')
        console.setFormatter(formatter)

        # Add handlers to the logger
        self.addHandler(console)

    def set_directory(self, log_dir):
        log_filename = datetime.now().strftime('%H_%M_%S_%d_%m_%Y.log')

        file_handler = logging.FileHandler(
            filename=log_dir + '/' + log_filename,
            mode='w'
        )

        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.addHandler(file_handler)

Logger = CtiOsLogger()

if __name__ == '__main__':
    # Logger.set_directory('/tmp')

    Logger.debug('debug')
    Logger.info('info')
    Logger.warning('warning')
    Logger.error('error')
    Logger.fatal('fatal')

    
