import argparse
import json
import socket
import sys
import time
from HW_7.log.errors import ServerError
from config import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, STATUS, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, SENDER, MESSAGE_TEXT, MESSAGE
from utils import get_message, send_message
from log.client_log_config import logger
from decor import log


@log
def message_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        logger.info(f'Получено сообщение от пользователя '
                    f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        logger.error(f'Получено некорректное сообщение с сервера: {message}')


@log
def create_message(sock, account_name='Guest'):
    message = input('Введите сообщение для отправки или \'Q\' для завершения работы: ')
    if message == 'Q':
        sock.close()
        logger.info('Завершение работы по команде пользователя.')
        print('Good bye!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    logger.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


@log
def create_presence(account_name='Guest', status='online'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
            STATUS: status
        }
    }
    logger.debug(f'Сообщение {out} для пользователя {account_name} сформировано')
    return out


@log
def process_ans(message):
    logger.info(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


@log
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')

    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    mode = namespace.mode
    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимые адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)
    if mode not in ('listen', 'send'):
        logger.critical(f'Указан недопустимый режим работы {mode}, '
                        f'допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, mode


@log
def main():
    server_address, server_port, mode = parse_args()

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, режим работы: {mode}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence())
        answer = process_ans(get_message(transport)).encode('utf-8')
        logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)

    else:
        if mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            if mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    logger.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)

            if mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    logger.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
