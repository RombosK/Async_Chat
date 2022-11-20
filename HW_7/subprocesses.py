from subprocess import Popen, CREATE_NEW_CONSOLE

process = []

while True:
    action = input("Запустить X клиентов (1-9) / Закрыть клиентов (x) / Выйти (q) ")

    if action == 'q':
        break
    elif action.isdigit():
        for _ in range(int(action)):
            process.append(Popen('python client.py',
                                 creationflags=CREATE_NEW_CONSOLE))
        print(' Запущено %s клиентов' % action)
    elif action == 'x':
        for p in process:
            p.kill()
        process.clear()
