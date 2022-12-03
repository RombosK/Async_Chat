import json

"""2. Модуль JSON. Есть файл orders в формате JSON с
информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными."""


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders_1.json', 'r', encoding='utf-8') as f_n:
        f_n_content = f_n.read()
        obj = json.loads(f_n_content)
    if obj and 'orders' in obj.keys():
        old_orders = obj['orders']
    else:
        old_orders = []
    new_order = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date,
    }

    old_orders.append(new_order)
    dict_to_json = {'orders': old_orders}
    with open('orders_1.json', 'w', encoding='utf-8') as f_n:
        f_n.write(json.dumps(dict_to_json, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    write_order_to_json('printer', '10', '6700', 'Ivanov I.I.', '24.09.2017')
    write_order_to_json('scaner', '20', '10000', 'Petrov P.P.', '11.01.2018')
    write_order_to_json('computer', '5', '40000', 'Sidorov S.S.', '2.05.2019')
    write_order_to_json('принтер', '10', '6700', 'Ivanov I.I.', '24.09.2017')
    write_order_to_json('сканер', '20', '10000', 'Petrov P.P.', '11.01.2018')
    write_order_to_json('компьютер', '5', '40000', 'Sidorov S.S.', '2.05.2019')
