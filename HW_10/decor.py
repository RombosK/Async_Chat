import logging
import sys
from functools import wraps
from log.client_log_config import logger
import inspect


if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


def log(func):
    @wraps(func)
    def callback(*args, **kwargs):
        res = func(*args, **kwargs)
        logger.debug('Function {} was called from {}'.format(func.__name__, inspect.stack()[1][3]))
        logger.debug('Function {}({}, {}), return {}'.format(func.__name__, args, kwargs, res))
        return res
    return callback

