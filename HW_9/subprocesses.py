import subprocess
from subprocess import Popen, CREATE_NEW_CONSOLE

processes = []

while True:
    action = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, '
                   'x - закрыть все окна: ')

    if action == 'q':
        break
    elif action == 's':
        processes.append(subprocess.Popen('python server.py',
                                          creationflags=CREATE_NEW_CONSOLE))
        processes.append(subprocess.Popen('python client.py -n test1',
                                          creationflags=CREATE_NEW_CONSOLE))
        processes.append(subprocess.Popen('python client.py -n test2',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'x':
        while processes:
            process = processes.pop()
            process.kill()
