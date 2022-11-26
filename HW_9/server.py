import sys
import select
import time
import argparse
import socket
from HW_9.decor import log
from config import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, DEFAULT_IP_ADDRESS, MESSAGE, SENDER, MESSAGE_TEXT, RESPONSE_OK, \
    RESPONSE_BAD, JET, EXIT
from utils import get_message, send_message
from log.server_log_config import server_logger


@log
def process_client_message(message, messages_list, client, clients, names):
    server_logger.debug(f'Processing client message : {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_OK)
        else:
            response = RESPONSE_BAD
            response[ERROR] = 'Такой пользователь уже существует'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
            JET in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return

    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        response = RESPONSE_BAD
        response[ERROR] = 'Неправильный запрос'
        send_message(client, response)
        return

@log
def process_message(message, names, listen_socks):
    if message[JET] in names and names[message[JET]] in listen_socks:
        send_message(names[message[JET]], message)
        server_logger.info(f'Отправлено сообщение пользователю {message[JET]} '
                    f'от пользователя {message[SENDER]}.')
    elif message[JET] in names and names[message[JET]] not in listen_socks:
        raise ConnectionError
    else:
        server_logger.error(
            f'Пользователь {message[JET]} не зарегистрирован,отправка сообщения невозможна. ')

@log
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.a
    server_port = namespace.p

    if not 1023 < server_port < 65536:
        server_logger.critical(
            f'Попытка запуска сервера с неподходящим портом {server_port}. Допустимые адреса с 1024 до 65535.')
        sys.exit(1)

    return server_address, server_port


def main():
    server_address, server_port = parse_args()

    server_logger.info(
        f'Запущен сервер, порт для подключений: {server_port}, '
        f'адрес, с которого принимаются подключения: {server_address}. '
        f'Если адрес не указан, принимаются любые соединения')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((server_address, server_port))
    transport.settimeout(1)
    server_logger.info("Запущено прослушивание порта %s" % str(server_port))
    clients = []
    messages = []
    names = dict()
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
                                               messages, client_with_message, clients, names)
                    except Exception as e:
                        server_logger.info(f'Клиент {client_with_message.getpeername()} '
                                           f'отключился от сервера.')
                        clients.remove(client_with_message)

            for i in messages:
                try:
                    process_message(i, names, send_data)
                except Exception as e:
                    server_logger.info(f'Связь с клиентом {i[JET]} была потеряна')
                    clients.remove(names[i[JET]])
                    del names[i[JET]]
            messages.clear()


if __name__ == '__main__':
    main()
