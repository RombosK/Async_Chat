
DEFAULT_IP_ADDRESS = '127.0.0.1'

DEFAULT_PORT = 7777

ENCODING = 'utf-8'

SERVER_CONFIG = 'server.ini'

MAX_CONNECTIONS = 5
MAX_SIZE_MSG = 1024

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
STATUS = 'status'
SENDER = 'from'
DESTINATION = 'to'
EXIT = 'exit'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
ALERT = 'alert'
OK = 'ok'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
GET_CONTACTS = 'get_contacts'
ADD_CONTACT = 'add_contact'
USER_ID = 'user_id'
DEL_CONTACT = 'del_contact'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
USERS_REQUEST = 'get_users'

RESPONSE_OK = {RESPONSE: 200}
RESPONSE_BAD = {
    RESPONSE: 400,
    ERROR: None
}


RESPONSE_202 = {
    RESPONSE: 202,
    ALERT: None
}

CONTACTS = {
    ACTION: None,
    TIME: None,
    ACCOUNT_NAME: None,
    USER_ID: None
}





