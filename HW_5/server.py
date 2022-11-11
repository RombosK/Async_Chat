import argparse
import socket
import json
from config import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, DEFAULT_IP_ADDRESS
from utils import get_message, send_message

"""Реализовать простое клиент-серверное взаимодействие по протоколу JIM (JSON instant
messaging):
b. сервер отвечает соответствующим кодом результата
Функции сервера:
● принимает сообщение клиента;
● формирует ответ клиенту;
● отправляет ответ клиенту;
● имеет параметры командной строки:
○ -p <port> — TCP-порт для работы (по умолчанию использует 7777);
○ -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все
доступные адреса)."""


def process_client_message(message):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'BAD REQUEST'
    }


def parse_args():
    parser = argparse.ArgumentParser(description='Server App')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                        help='enter port number')
    parser.add_argument('-a', '--addr', default=DEFAULT_IP_ADDRESS, type=str,
                        help='enter IP address')
    return parser.parse_args()


def main():
    args = parse_args()
    port = args.port
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind(("", port))
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            response = process_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорретное сообщение от клиента.')
            client.close()


if __name__ == '__main__':
    main()
