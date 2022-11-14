import argparse
import socket
import json
from config import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, DEFAULT_IP_ADDRESS
from utils import get_message, send_message
from log.server_log_config import server_logger


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
    try:
        port = args.port
    except ValueError as e:
        return server_logger.error(e)
    try:
        server_address = DEFAULT_IP_ADDRESS
    except ValueError as er:
        return server_logger.error(er)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind(("", port))
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        server_logger.info(f'Установлено соедение с клиентом {client_address}')
        try:
            message_from_client = get_message(client)
            server_logger.debug(f'Получено сообщение {message_from_client}')
            print(message_from_client)
            response = process_client_message(message_from_client)
            server_logger.info(f'Cформирован ответ клиенту {response}')
            send_message(client, response)
            server_logger.debug(f'Соединение с клиентом {client_address} закрывается.')
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорретное сообщение от клиента.')
            client.close()


if __name__ == '__main__':
    main()
