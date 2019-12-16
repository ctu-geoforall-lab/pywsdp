import logging
from datetime import datetime
import os


class Logger:

    def __init__(self, name='pyctios', log_dir=None):
        logger = logging.getLogger(name)

        if log_dir and os.path.isabs(log_dir):

            log_filename = datetime.now().strftime('%H_%M_%S_%d_%m_%Y.log')

            # Basic configuration of log file
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename=log_dir + '/' + log_filename,
                                filemode='w')

        # Define a Stream Console Handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        # Create formats and add it to console handler
        formatter = logging.Formatter('%(name)-12s - %(levelname)-8s - %(message)s')
        console.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(console)

        self.logger = logger

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def fatal(self, msg):
        self.logger.fatal(msg)


if __name__ == '__main__':
    log = Logger()
    log.debug('debug')
    log.info('info')
    log.warning('warning')
    log.error('error')
    log.fatal('fatal')