import logging
from functools import wraps
from HW_6.log.client_log_config import logger
import log.server_log_config
import traceback
import inspect


def log(func):
    @wraps(func)
    def callback(*args, **kwargs):
        res = func(*args, **kwargs)
        logger.debug('Function {} was called from {}'.format(func.__name__, inspect.stack()[1][3]))
        logger.debug('Function {}({}, {}), return {}'.format(func.__name__, args, kwargs, res))
        return res
    return callback


