""" 2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только последний
 октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение."""

from ipaddress import ip_address
from ex_1 import host_ping


def host_range_ping():
    while True:
        start = input('Введите стартовый ip-адрес: ')
        try:
            edge_dig = int(start.split('.')[3])
            break
        except Exception as ex:
            print(ex)
    while True:
        end = input('Введите кол-во ip-aдресов для поверки: ')
        if not end.isnumeric():
            print('Введите число: ')
        else:
            if (edge_dig + int(end)) > 254:
                print(f"максимальное число хостов для проверки: {254 - edge_dig}")
            else:
                break

    hosts = []
    [hosts.append(str(ip_address(start) + x)) for x in range(int(end))]
    return host_ping(hosts)


if __name__ == "__main__":
    host_range_ping()




