import argparse
import json
import socket
import sys
import time
import logging
import threading
from log.errors import ServerError, IncorrectDataRecivedError
from config import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, STATUS, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, SENDER, MESSAGE_TEXT, MESSAGE, ENCODING, EXIT, JET
from utils import get_message, send_message
from log.client_log_config import logger
from decor import log


@log
def exit_msg(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        STATUS: STATUS
    }


@log
def message_from_server(sock, my_username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and JET in message \
                    and MESSAGE_TEXT in message and message[JET] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                logger.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                            f'\n{message[MESSAGE_TEXT]}')
            else:
                logger.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            logger.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            logger.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_message(sock, account_name='Guest'):
    to_user = input('Введите username получателя=> ')
    message = input('Введите сообщение для отправки или \'q\' для завершения работы: ')
    if message == 'Q':
        sock.close()
        logger.info('Завершение работы по команде пользователя.')
        print('Good bye!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        JET: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    logger.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        logger.info(f'Отправлено сообщение пользователю {to_user}')
    except:
        logger.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@log
def user_active(sock, username):
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'exit':
            send_message(sock, exit_msg(username))
            print('Закрытие соединения.')
            logger.info('Завершение работы клиента по команде пользователя.')
            time.sleep(1)
            break
        else:
            print('Команда не распознана, попробойте снова.')

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
    parser.add_argument('-n', '--name', default=None, nargs='?')

    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    name = namespace.name
    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим портом: {server_port}. '
            f'Допустимые адреса с 1024 до 65535. Клиент закрывается.')
        sys.exit(1)

    return server_address, server_port, name


def main():
    print('Starting client')
    server_address, server_port, name = parse_args()

    if not name:
        name = input('Введите имя пользователя=> ')

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя пользователя: {name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(name))
        answer = process_ans(get_message(transport)).encode(ENCODING)
        logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный client отверг запрос на подключение.')
        sys.exit(1)

    else:
        receiver = threading.Thread(target=message_from_server, args=(transport, name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=user_active, args=(transport, name))
        user_interface.daemon = True
        user_interface.start()
        logger.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
