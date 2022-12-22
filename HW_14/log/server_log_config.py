import logging
import os.path
from logging.handlers import TimedRotatingFileHandler

formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s ")

path = os.path.join(os.path.abspath(__file__), '..', "server.log")

server_logger = logging.getLogger('server')


F_H = logging.handlers.TimedRotatingFileHandler(path, when='D', interval=1, backupCount=5, encoding='utf-8')
F_H.setLevel(logging.DEBUG)
F_H.setFormatter(formatter)

server_logger.addHandler(F_H)
server_logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    server_logger.info('status')
    server_logger.debug('Отладочная информация')



