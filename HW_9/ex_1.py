"""1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
 В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
 («Узел доступен», «Узел недоступен»).
  При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address()."""

from ipaddress import ip_address
from subprocess import Popen, PIPE
import platform

is_win = platform.system().lower() == 'windows'
param = '-n' if is_win else '-c'


def host_ping(hosts_lst, timeout=500, requests=1):
    results = dict(Reachable="", Unreachable="")
    for host in hosts_lst:
        try:
            host = ip_address(host)
        except ValueError:
            host = host
        check = Popen(f"ping {host} -w {timeout} -n {requests}", shell=is_win, stdout=PIPE, stderr=PIPE)
        check.wait()
        if check.returncode == 0:
            results['Reachable'] += f"{str(host)}\n"
            result = f'{host} - Узел доступен'
        else:
            results['Unreachable'] += f"{str(host)}\n"
            result = f'{host} - Узел недоступен'
        print(result)
    return results


if __name__ == '__main__':
    hosts = ['github.com', '1.1.1.1', '127.0.0.1', '77.88.21.15', 'www.ok.kz']
    host_ping(hosts)


