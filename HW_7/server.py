import logging
import sys

import select
import time
import argparse
import socket
import json
from HW_7.decor import log
from config import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, DEFAULT_IP_ADDRESS, MESSAGE, SENDER, MESSAGE_TEXT
from utils import get_message, send_message
from log.server_log_config import server_logger


@log
def process_client_message(message):
    server_logger.debug(f'Processing client message : {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'BAD REQUEST'
    }


# @log
# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, nargs='?',
#                         help='enter port number')
#     parser.add_argument('-a', '--addr', default='', nargs='?',
#                         help='enter IP address')
#     return parser.parse_args()
@log
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        server_logger.critical(
            f'Попытка запуска сервера с указанием неподходящего порта '
            f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port


@log
def main():
    server_address, port = parse_args()

    server_logger.info(
        f'Запущен сервер, порт для подключений: {port}, '
        f'адрес с которого принимаются подключения: {server_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')
    # args = parse_args()
    # try:
    #     port = args.port
    # except ValueError as e:
    #     return server_logger.error(e)
    # try:
    #     server_address = args.addr
    # except ValueError as er:
    #     return server_logger.error(er)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((server_address, port))
    transport.settimeout(1)
    server_logger.info("Запущено прослушивание порта %s" % str(port))
    clients = []
    messages = []
    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError as e:
            pass
        else:
            server_logger.info(f'Установлено соедение с клиентом {client_address}')
            clients.append(client)
        finally:
            waiting_client = 0
            recv_data = []
            send_data = []
            err_data = []

            try:
                if clients:
                    recv_data, send_data, err_data = select.select(clients, clients, [], waiting_client)
            except OSError:
                pass
            if recv_data:
                for client_with_message in recv_data:
                    try:
                        process_client_message(get_message(client_with_message),
                                               messages, client_with_message)
                    except:
                        server_logger.info(f'Клиент {client_with_message.getpeername()} '
                                           f'отключился от сервера.')
                        clients.remove(client_with_message)

            if messages and send_data:
                message = {
                    ACTION: MESSAGE,
                    SENDER: messages[0][0],
                    TIME: time.time(),
                    MESSAGE_TEXT: messages[0][1]
                }
                del messages[0]
                for waiting_client in send_data:
                    try:
                        send_message(waiting_client, message)
                    except:
                        server_logger.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                        clients.remove(waiting_client)

        # try:
        #     message_from_client = get_message(client)
        #     server_logger.debug(f'Получено сообщение {message_from_client}')
        #     print(message_from_client)
        #     response = process_client_message(message_from_client)
        #     server_logger.info(f'Cформирован ответ клиенту {response}')
        #     send_message(client, response)
        #     server_logger.debug(f'Соединение с клиентом {client_address} закрывается.')
        #     client.close()
        # except (ValueError, json.JSONDecodeError):
        #     print('Принято некорретное сообщение от клиента.')
        #     client.close()


if __name__ == '__main__':
    main()
