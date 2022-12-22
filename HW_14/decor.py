import inspect
import logging
import socket
import sys
from functools import wraps
from HW_14.log.server_log_config import server_logger

if sys.argv[0].find('client') == -1:
    server_logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


def log(func):
    @wraps(func)
    def callback(*args, **kwargs):
        res = func(*args, **kwargs)
        server_logger.debug('Function {} was called from {}'.format(func.__name__, inspect.stack()[1][3]))
        server_logger.debug('Function {}({}, {}), return {}'.format(func.__name__, args, kwargs, res))
        return res

    return callback


def login_required(func):
    """Декоратор @login_required, проверяющий авторизованность пользователя для выполнения той или иной функции."""
    def checker(*args, **kwargs):
        from server.core import MessageProcessor
        from config import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
