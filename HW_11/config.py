
DEFAULT_IP_ADDRESS = '127.0.0.1'

DEFAULT_PORT = 7777

ENCODING = 'utf-8'

MAX_CONNECTIONS = 5
MAX_SIZE_MSG = 1024

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
STATUS = 'status'
SENDER = 'from'
JET = 'to'
EXIT = 'exit'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
OK = 'ok'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'

RESPONSE_OK = {RESPONSE: 200}
RESPONSE_BAD = {
    RESPONSE: 400,
    ERROR: None
}



