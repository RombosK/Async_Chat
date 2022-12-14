import sys
import logging
import argparse
import log.client_log_config
from PyQt6.QtWidgets import QApplication
from config import *
from decor import log
from log.errors import ServerError
from client.transport import ClientTransport
from client.database import ClientDataBase
from client.start_dialog import UserNameDialog
from client.main_window import ClientMainWindow

logger = logging.getLogger('client')


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
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимые адреса с 1024 до 65535.\n'
            f' Клиент завершается')
        exit(1)
    return server_address, server_port, client_name


if __name__ == '__main__':
    server_address, server_port, client_name = arg_parser()
    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)
    logger.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address}, порт: {server_port},\n'
        f' имя пользователя: {client_name}')
    database = ClientDataBase(client_name)
    try:
        transport = ClientTransport(server_port, server_address, database, client_name)
    except ServerError as error:
        print(error.text)
        exit(1)

    transport.setDaemon(True)
    transport.start()

    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Chat - {client_name}')
    client_app.exec()
    transport.transport_shutdown()
    transport.join()
