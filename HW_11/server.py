import sys
import select
import time
import argparse
import socket
from decor import log
from config import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, DEFAULT_IP_ADDRESS, MESSAGE, SENDER, MESSAGE_TEXT, RESPONSE_OK, \
    RESPONSE_BAD, JET, EXIT
from utils import get_message, send_message
from log.server_log_config import server_logger
from descriptor import Port, Host
from meta_cls import ServerVerifier


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
    addr = Host()

    def __init__(self, listen_address, listen_port):
        self.addr = listen_address
        self.port = listen_port
        self.clients = []
        self.messages = []
        self.names = dict()

    def init_socket(self):
        server_logger.info(
            f'Запущен сервер, порт для подключений: {self.port} , адрес,с которого принимаются подключения: {self.addr}.\
             Если адрес не указан, принимаются соединения с любых адресов.')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen(MAX_CONNECTIONS)

    def main_loop(self):
        self.init_socket()

        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                server_logger.info(f'Установлено соедение с клиентом {client_address}')
                self.clients.append(client)

            recv_data = []
            send_data = []
            err_data = []
            try:
                if self.clients:
                    recv_data, send_data, err_data = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data:
                for client_with_message in recv_data:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        server_logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            for messages in self.messages:
                try:
                    self.process_message(messages, send_data)
                except:
                    server_logger.info(f'Связь с клиентом  {messages[JET]} была потеряна.')
                    self.clients.remove(self.names[messages[JET]])
                    del self.names[messages[JET]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        if message[JET] in self.names and self.names[message[JET]] in listen_socks:
            send_message(self.names[message[JET]], message)
            server_logger.info(f'Отправлено сообщение пользователю {message[JET]} от пользователя {message[SENDER]}.')
        elif message[JET] in self.names and self.names[message[JET]] not in listen_socks:
            raise ConnectionError
        else:
            server_logger.error(
                f'Пользователь {message[JET]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    def process_client_message(self, message, client):
        server_logger.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_OK)
            else:
                response = RESPONSE_BAD
                response[ERROR] = 'Имя пользователя занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and JET in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
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





