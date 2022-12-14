import argparse
import json
import socket
import sys
import time
import logging
import threading
from log.errors import ServerError, IncorrectDataRecivedError, ReqFieldMissingError
from HW_13.config import *
from HW_13.utils import get_message, send_message
from log.client_log_config import logger
from decor import log
from meta_cls import ClientVerifier
from db_client import UserDatabase


sock_lock = threading.Lock()
database_lock = threading.Lock()


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        self.db = UserDatabase(account_name)
        super().__init__()

    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def get_contacts(self):
        message_dict = {
            ACTION: GET_CONTACTS,
            ACCOUNT_NAME: self.account_name,
            TIME: time.time(),
        }
        send_message(self.sock, message_dict)

    def add_contact(self):
        message_dict = CONTACTS
        message_dict[ACTION] = ADD_CONTACT
        message_dict[TIME] = time.time()
        message_dict[ACCOUNT_NAME] = self.account_name
        message_dict[USER_ID] = input('Введите имя пользователя для добавления в контакт-лист: ')
        send_message(self.sock, message_dict)
        self.db.add_contact(message_dict[USER_ID])

    def del_contact(self):
        message_dict = CONTACTS
        message_dict[ACTION] = DEL_CONTACT
        message_dict[TIME] = time.time()
        message_dict[ACCOUNT_NAME] = self.account_name
        message_dict[USER_ID] = input('Введите имя пользователя для удаления из контакт-листа: ')
        send_message(self.sock, message_dict)
        self.db.del_contact(message_dict[USER_ID])

    def create_message(self):
        to = input('Введите имя получателя сообщения: ')
        message = input('Введите сообщение: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            logger.info(f'Отправлено сообщение для пользователя {to}')
        except:
            logger.critical('Потеряно соединение с сервером.')
            exit(1)

    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    print(':)')
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            elif command == 'contacts':
                self.get_contacts()
            elif command == 'add':
                self.add_contact()
            elif command == 'del':
                self.del_contact()
            else:
                print('Команда не распознана, попробyйте снова. help - вывести поддерживаемые команды.')

    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')
        print('contacts - получить список контактов')
        print('add - добавить пользователя в контакт-лист')
        print('del - удалить пользователя из контакт-листа')


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and JET in message \
                        and MESSAGE_TEXT in message and message[JET] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    logger.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                elif RESPONSE in message and message[RESPONSE] == 202:
                    print(f'Список контактов: {message[ALERT]}')
                elif RESPONSE in message and message[RESPONSE] == 200:
                    print(f'Операция выполнена успешно')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                logger.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break


@log
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def process_ans(message):
    logger.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        logger.critical(
            f'Неподходящий порт: {server_port}. Допустимые адреса с 1024 до 65535.')
        exit(1)

    return server_address, server_port, client_name


def main():
    print('Консольный месседжер.')

    server_address, server_port, client_name = arg_parser()

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_ans(get_message(transport))
        logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный сервер отклонтл запрос.')
        exit(1)
    else:
        receiver = ClientReader(client_name, transport)
        receiver.daemon = True
        receiver.start()

        user_active = ClientSender(client_name, transport)
        user_active.daemon = True
        user_active.start()
        logger.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_active.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
