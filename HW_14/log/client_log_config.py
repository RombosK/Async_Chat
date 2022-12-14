import logging
import os.path
from logging.handlers import TimedRotatingFileHandler

path = os.path.join(os.path.abspath(__file__), '..', "client.log")

logger = logging.getLogger('client')

formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s ")

F_H = logging.handlers.TimedRotatingFileHandler(path, when='D', backupCount=5, encoding='utf-8')
F_H.setLevel(logging.DEBUG)
F_H.setFormatter(formatter)

logger.addHandler(F_H)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    logger.info('Starting client')
    logger.debug('Отладочная информация')
