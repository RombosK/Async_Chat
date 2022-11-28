import yaml

"""3. Модуль YAML. Написать скрипт, автоматизирующий
сохранение данных в файле YAML-формата."""

main_data = {'items': ['computer', 'printer', 'scaner'],
           'items_quantity': 3,
           'items_ptice': {'computer': '800€-1000€',
                           'printer': '200€-400€',
                           'scaner': '180€-300€'}
             }
with open('file.yaml', 'w', encoding='utf-8') as f_n:
    yaml.dump(main_data, f_n, default_flow_style=False, allow_unicode=True)

with open("file.yaml", 'r', encoding='utf-8') as f_s:
    new_data = yaml.load(f_s, Loader=yaml.SafeLoader)

print(main_data == new_data)






