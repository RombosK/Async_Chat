import argparse
import json
import socket
import time
from config import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, STATUS, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from utils import get_message, send_message

"""Реализовать простое клиент-серверное взаимодействие по протоколу JIM (JSON instant
messaging):
a. клиент отправляет запрос серверу;
Функции клиента:
● сформировать presence-сообщение;
● отправить сообщение серверу;
● получить ответ сервера;
● разобрать сообщение сервера;
● параметры командной строки скрипта client.py <addr> [<port>]:
○ addr — ip-адрес сервера;
○ port — tcp-порт на сервере, по умолчанию 7777."""


def create_presence(account_name='Guest', status=None):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
            STATUS: status
        }
    }
    return out


def process_ans(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    parser = argparse.ArgumentParser(description='ClientAddress')
    parser_group = parser.add_argument_group(title=None)
    parser_group.add_argument(
        '-a', '--addr', default=DEFAULT_IP_ADDRESS, help='IP address')
    parser_group.add_argument('-p', '--port', type=int,
                              default=DEFAULT_PORT, help='Open port')
    return parser
    namespace = parser.parse_args()
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((namespace.addr, namespace.port))
    message_to_server = create_presence()
    send_message(transport, message_to_server)
    try:
        answer = process_ans(get_message(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
