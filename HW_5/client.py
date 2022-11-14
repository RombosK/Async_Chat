import argparse
import json
import socket
import time
from config import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, STATUS, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from utils import get_message, send_message
from log.client_log_config import logger


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


def process_ans(message):
    logger.info(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def parse_args():
    parser = argparse.ArgumentParser(description='Client App')
    parser.add_argument('-a', '--addr', default=DEFAULT_IP_ADDRESS, type=str,
                        help='enter IP address')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                        help='enter port number')
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        port = args.port
    except ValueError as e:
        return logger.error(e)
    try:
        server_address = DEFAULT_IP_ADDRESS
    except ValueError as er:
        return logger.error(er)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, port))
    logger.info('Соединение с сервером установлено')
    message_to_server = create_presence()
    logger.info('Запрос отправлен')
    send_message(transport, message_to_server)
    try:
        answer = process_ans(get_message(transport))
        logger.info('Ответ получен')
        logger.info(f'Ответ {answer} успешно обработан')
        print(answer)

    except ValueError:
        logger.error('Программный сбой')


if __name__ == '__main__':
    main()
