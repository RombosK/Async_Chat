import argparse
import select
import socket
import sys
from descriptor import Port, Host
from log.server_log_config import server_logger
from decor import log
from meta_cls import ServerVerifier
from utils import get_message, send_message
from config import *
from db_server import ServerDataBase


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


class Server(metaclass=ServerVerifier):
    port = Port()
    host = Host()

    def __init__(self, listen_address, listen_port):
        self.addr = listen_address
        self.port = listen_port
        self.clients = []
        self.messages = []
        self.names = dict()
        self.db = ServerDataBase()

    def init_socket(self):
        server_logger.info(
            f'Запущен сервер, порт для подключений: {self.port} , '
            f'адрес с которого принимаются подключения: {self.addr}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)
        self.sock = transport
        self.sock.listen()

    def main_loop(self):
        self.init_socket()
        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                server_logger.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    server_logger.info(f'Связь с клиентом {message[DESTINATION]} потеряна')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            server_logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            server_logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    def process_client_message(self, message, client):
        server_logger.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_OK)
                self.db.add_user(message[USER][ACCOUNT_NAME])
            else:
                response = RESPONSE_BAD
                response[ERROR] = 'Имя пользователя занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            print('On-line')
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            print(self.names)
            del self.names[message[ACCOUNT_NAME]]
            print(self.names)
            return
        elif ACTION in message and message[ACTION] == GET_CONTACTS and TIME in message and ACCOUNT_NAME in message and \
                self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[ALERT] = self.db.get_contacts(message[ACCOUNT_NAME])
            send_message(client, response)
            return
        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and \
                self.names[message[ACCOUNT_NAME]] == client and USER_ID in message:
            self.db.add_contact(message[ACCOUNT_NAME], message[USER_ID])
            send_message(client, RESPONSE_OK)
        elif ACTION in message and message[ACTION] == DEL_CONTACT and ACCOUNT_NAME in message and \
                self.names[message[ACCOUNT_NAME]] == client and USER_ID in message:
            self.db.del_contact(message[ACCOUNT_NAME], message[USER_ID])
            send_message(client, RESPONSE_OK)
        else:
            response = RESPONSE_BAD
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return


def main():
    listen_address, listen_port = arg_parser()
    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
