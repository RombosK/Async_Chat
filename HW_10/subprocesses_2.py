import random
import subprocess
import time
from subprocess import Popen, CREATE_NEW_CONSOLE
process = []


def get_name(i):
    return f'{random.getrandbits(128)}/{i}'


while True:
    action = input('Выберите действие: q - выход , s - запустить сервер и клиенты, x - закрыть все окна:')

    if action == 'q':
        break
    elif action == 's':

        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        process.append(subprocess.Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))

        time.sleep(0.5)
        for i in range(clients_count):
            name = get_name(i)
            process.append(subprocess.Popen(f'python client.py -n Test{name}', shell=True))
    elif action == 'x':
        while process:
            victim = process.pop()
            victim.terminate()
            victim.kill()
